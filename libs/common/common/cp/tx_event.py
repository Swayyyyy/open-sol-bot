import asyncio
from typing import Any, Callable, Coroutine, Optional

import aioredis

from common.log import logger
from common.types.tx import TxEvent

NEW_TX_EVENT_CHANNEL = "tx_event:new"


class TxEventProducer:
    def __init__(self, redis_client: aioredis.Redis) -> None:
        self.redis = redis_client

    async def produce(self, tx_event: TxEvent) -> None:
        """Produces a transaction event to Redis Stream.

        Args:
            tx_event: Transaction event data as string
        """
        try:
            await self.redis.xadd(
                name=NEW_TX_EVENT_CHANNEL,
                fields={"data": tx_event.to_json()},
                maxlen=10000,  # Keep last 10k events
            )
        except Exception as e:
            # Log error but don't re-raise to avoid disrupting the producer
            logger.error(f"Error producing tx event to Redis Stream: {e}")


class TxEventConsumer:
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
        """
        self.redis = redis_client
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.batch_size = batch_size
        self.poll_timeout_ms = poll_timeout_ms
        self.is_running = False
        self.callback: Optional[Callable[[TxEvent], Coroutine[Any, Any, None]]] = None
        self.task_pool = set()
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def setup(self) -> None:
        """Setup the consumer group if it doesn't exist."""
        try:
            # Create consumer group if not exists
            # Use $ as start ID to only process new messages
            await self.redis.xgroup_create(
                name=NEW_TX_EVENT_CHANNEL,
                groupname=self.consumer_group,
                mkstream=True,
                id="$",
            )
        except aioredis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
            logger.info(f"Consumer group {self.consumer_group} already exists")

    def register_callback(
        self, callback: Callable[[TxEvent], Coroutine[Any, Any, None]]
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
                streams={NEW_TX_EVENT_CHANNEL: "0"},  # 0 means all pending messages
                count=self.batch_size,
            )

            if pending and self.callback:
                for _, messages in pending:
                    for message_id, fields in messages:
                        try:
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
        try:
            if self.callback is not None:
                data = fields["data"]
                if data is None:
                    logger.warning(f"Data is None, message_id: {message_id}")
                    return
                tx_event = TxEvent.from_json(data)
                await self.callback(tx_event)
            # Acknowledge the message
            await self.redis.xack(NEW_TX_EVENT_CHANNEL, self.consumer_group, message_id)
        except Exception as e:
            logger.exception(f"Error processing message {message_id}: {e}")
            # Could implement retry logic here

    def _create_task(self, message_id: str, fields: dict) -> None:
        """创建新的异步任务来处理消息"""
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
                    streams={NEW_TX_EVENT_CHANNEL: ">"},  # > means new messages only
                    count=self.batch_size,
                    block=self.poll_timeout_ms,
                )

                if messages:
                    for stream, stream_messages in messages:
                        for message_id, fields in stream_messages:
                            self._create_task(message_id, fields)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error reading from stream: {e}")
                await asyncio.sleep(1)  # Avoid tight loop on errors

    def stop(self) -> None:
        """Stop consuming messages."""
        self.is_running = False
