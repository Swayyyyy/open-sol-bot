from aioredis import Redis
from common.config import settings
from common.log import logger


class RedisClient:
    _instance: Redis | None = None

    @classmethod
    def get_instance(cls) -> Redis:
        if cls._instance is None:
            try:
                cls._instance = Redis.from_url(
                    str(settings.db.redis), encoding="utf-8", decode_responses=True
                )
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
            logger.info("Redis connection closed")
