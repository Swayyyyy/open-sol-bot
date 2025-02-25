from datetime import timedelta

import aioredis
from spl.token.async_client import AsyncToken

from cache.auto.base import BaseAutoUpdateCache
from common.log import logger
from common.utils import get_async_client
from db.redis import RedisClient


class MinBalanceRentCache(BaseAutoUpdateCache):
    key = "min_balance_rent"

    def __init__(self, redis: aioredis.Redis):
        self.client = get_async_client()
        self.redis = redis
        super().__init__(redis)

    async def _gen_new_value(self) -> int:
        """更新最小租金余额"""
        min_balance = await AsyncToken.get_min_balance_rent_for_exempt_for_account(
            self.client
        )
        return min_balance

    @classmethod
    async def get(cls, redis: aioredis.Redis | None = None) -> int:
        """获取最小租金余额"""
        redis = redis or RedisClient.get_instance()
        cached_value = await redis.get(cls.key)
        if cached_value is None:
            logger.warning("Min balance rent cache not found, updating...")
            min_balance_rent_cache = cls(redis)
            cached_value = await min_balance_rent_cache._gen_new_value()
            await redis.set(cls.key, cached_value, ex=timedelta(seconds=30))
        return int(cached_value)
