import asyncio
import time
from typing import Any, Callable, Coroutine

import aioredis

from common.log import logger
from common.types import SwapEvent

SWAP_EVENT_CHANNEL = "swap_event:new"
DEAD_LETTER_CHANNEL = "swap_event:dlq"
MAX_PROCESS_TIME = 15  # s


class SwapEventProducer:
    def __init__(self, redis_client: aioredis.Redis) -> None:
        self.redis = redis_client

    async def produce(self, swap_event: SwapEvent) -> None:
        """Produces a swap event to Redis Stream.

        Args:
            swap_event: Swap event data as string
        """
        try:
            await self.redis.xadd(
                name=SWAP_EVENT_CHANNEL,
                fields={"data": swap_event.to_json(), "timestamp": int(time.time())},
                maxlen=10000,  # Keep last 10k events
            )
        except Exception as e:
            # Log error but don't re-raise to avoid disrupting the producer
            logger.error(
                f"Error producing swap event to Redis Stream: {e}, raw: {swap_event}"
            )

        return


class SwapEventConsumer:
    def __init__(
        self,
        redis_client: aioredis.Redis,
        consumer_group: str,
        consumer_name: str,
        batch_size: int = 10,
        poll_timeout_ms: int = 5000,
        max_concurrent_tasks: int = 10,
    ) -> None:
        """Initialize the transaction event consumer.

        Args:
            redis_client: Redis client instance
            consumer_group: Name of the consumer group
            consumer_name: Unique name for this consumer instance
            batch_size: Number of events to process in one batch
            poll_timeout_ms: Timeout in milliseconds for blocking read
            max_concurrent_tasks: Maximum number of concurrent tasks
        """
        self.redis = redis_client
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.batch_size = batch_size
        self.poll_timeout_ms = poll_timeout_ms
        self.is_running = False
        self.callback: Callable[[SwapEvent], Coroutine[Any, Any, None]] | None = None
        self.task_pool = set()
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def setup(self) -> None:
        """Setup the consumer group if it doesn't exist."""
        try:
            # Create consumer group if not exists
            # Use $ as start ID to only process new messages
            await self.redis.xgroup_create(
                name=SWAP_EVENT_CHANNEL,
                groupname=self.consumer_group,
                mkstream=True,
                id="$",
            )
        except aioredis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
            logger.info(f"Consumer group {self.consumer_group} already exists")

    def register_callback(
        self, callback: Callable[[SwapEvent], Coroutine[Any, Any, None]]
    ) -> None:
        """Register a callback function to process events.

        Args:
            callback: Function that takes a dictionary of event data and processes it
        """
        self.callback = callback

    async def process_pending(self) -> None:
        """Process any pending messages for this consumer."""
        try:
            # Read pending messages from > start
            pending = await self.redis.xreadgroup(
                groupname=self.consumer_group,
                consumername=self.consumer_name,
                streams={SWAP_EVENT_CHANNEL: "0"},  # 0 means all pending messages
                count=self.batch_size,
            )

            if pending and self.callback:
                for _, messages in pending:
                    for message_id, fields in messages:
                        try:
                            logger.info(f"Processing pending message {message_id}")
                            await self._process_message(message_id, fields)
                        except Exception as e:
                            logger.error(
                                f"Error processing pending message {message_id}: {e}"
                            )
        except Exception as e:
            logger.error(f"Error processing pending messages: {e}")

    async def _process_message(self, message_id: str, fields: dict) -> None:
        """Process a single message and acknowledge it.

        Args:
            message_id: ID of the message in Redis Stream
            fields: Message fields containing the event data
        """
        async with self.semaphore:
            try:
                timestamp = float(fields.get("timestamp", 0))
                if time.time() - timestamp > MAX_PROCESS_TIME:
                    logger.warning(
                        f"Message {message_id} is too old, discard it. Timestamp: {timestamp}"
                    )
                elif self.callback is not None:
                    swap_event = SwapEvent.from_json(fields["data"])
                    await self.callback(swap_event)

                # Acknowledge the message
                await self.redis.xack(
                    SWAP_EVENT_CHANNEL, self.consumer_group, message_id
                )
            except Exception as e:
                logger.exception(f"Error processing message {message_id}: {e}")
                await self._move_to_dead_letter(message_id, fields, str(e))

    async def _move_to_dead_letter(
        self, message_id: str, fields: dict, error: str
    ) -> None:
        """Move a message to the dead letter queue.

        Args:
            message_id: Original message ID
            fields: Message fields
            error: Error message
        """
        fields["original_id"] = message_id
        fields["error"] = error
        fields["moved_to_dlq_at"] = str(time.time())

        try:
            # Add to dead letter queue
            await self.redis.xadd(DEAD_LETTER_CHANNEL, fields)
            # Acknowledge the original message
            await self.redis.xack(SWAP_EVENT_CHANNEL, self.consumer_group, message_id)
            # Delete the message from original stream
            await self.redis.xdel(SWAP_EVENT_CHANNEL, message_id)
            logger.info(
                f"Message {message_id} moved to dead letter queue and deleted from original stream"
            )
        except Exception as e:
            logger.error(f"Error moving message {message_id} to dead letter queue: {e}")
            raise

    def _create_task(self, message_id: str, fields: dict) -> None:
        """创建新的异步任务来处理消息"""
        logger.info(f"Creating task for message {message_id}")
        task = asyncio.create_task(self._process_message(message_id, fields))
        self.task_pool.add(task)
        task.add_done_callback(self.task_pool.discard)

    async def start(self) -> None:
        """Start consuming messages from the stream."""
        if not self.callback:
            raise ValueError("No callback registered. Call register_callback first.")

        await self.setup()
        self.is_running = True

        # First process any pending messages
        await self.process_pending()

        # Then start processing new messages
        while self.is_running:
            try:
                # Read new messages
                messages = await self.redis.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={SWAP_EVENT_CHANNEL: ">"},  # > means new messages only
                    count=self.batch_size,
                    block=self.poll_timeout_ms,
                )

                if messages is None:
                    continue

                for stream, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        self._create_task(message_id, fields)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error reading from stream: {e}")
                await asyncio.sleep(1)

    async def stop(self) -> None:
        """Stop consuming messages and wait for all tasks to complete."""
        self.is_running = False
        if self.task_pool:
            logger.info(f"Waiting for {len(self.task_pool)} tasks to complete...")
            await asyncio.gather(*self.task_pool, return_exceptions=True)
            logger.info("All tasks completed")
