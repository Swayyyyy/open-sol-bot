from db.redis import RedisClient
from asyncio.queues import Queue
from common.log import logger


class BenchmarkService:
    _instance: "BenchmarkService" = None  # type: ignore

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.q = Queue()
        self.redis = None

    async def connect_redis(self):
        self.redis = await RedisClient.get_instance()

    async def add(self, item):
        await self.q.put(item)

    async def process(self):
        while True:
            try:
                assert self.redis is not None, "Redis is not connected"
                await self.redis.ping()
            except AssertionError:
                await self.connect_redis()

            try:
                item = await self.q.get()
                if isinstance(item, dict) and self.redis is not None:
                    tx_hash = item.get("tx_hash")
                    step = item.get("step")
                    timestamp = item.get("timestamp")
                    if tx_hash and step and timestamp:
                        await self.redis.hset(
                            f"benchmark:{tx_hash}", step, str(timestamp)
                        )
                self.q.task_done()
            except Exception as e:
                logger.error(f"Error processing item: {e}")

    async def start(self):
        await self.connect_redis()
        await self.process()

    async def stop(self):
        await self.q.join()

    async def get_timeline(self, tx_hash: str) -> dict:
        """Get the timeline of a transaction's processing steps"""
        if self.redis is None:
            await self.connect_redis()
        assert self.redis is not None, "Redis is not connected"
        result = await self.redis.hgetall(f"benchmark:{tx_hash}")
        return {k: v for k, v in result.items()} if result else {}

    async def clear_timeline(self, tx_hash: str):
        """Clear the timeline data for a specific transaction"""
        if self.redis is None:
            await self.connect_redis()
        assert self.redis is not None, "Redis is not connected"
        await self.redis.delete(f"benchmark:{tx_hash}")


benchmark_service = BenchmarkService()
