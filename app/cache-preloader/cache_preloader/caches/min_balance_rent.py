from datetime import timedelta

import aioredis
from solbot_cache.constants import MIN_BALANCE_RENT_CACHE_KEY
from solbot_common.log import logger
from solbot_common.utils import get_async_client
from solbot_db.redis import RedisClient
from spl.token.async_client import AsyncToken

from cache_preloader.core.base import BaseAutoUpdateCache


class MinBalanceRentCache(BaseAutoUpdateCache):
    """最小租金余额缓存管理器"""

    key = MIN_BALANCE_RENT_CACHE_KEY

    def __init__(self, redis: aioredis.Redis):
        """
        初始化最小租金余额缓存管理器

        Args:
            redis: Redis客户端实例
        """
        self.client = get_async_client()
        self.redis = redis
        super().__init__(redis)

    async def _gen_new_value(self) -> int:
        """
        生成新的缓存值

        Returns:
            最小租金余额
        """
        min_balance = await AsyncToken.get_min_balance_rent_for_exempt_for_account(self.client)
        return min_balance

    @classmethod
    async def get(cls, redis: aioredis.Redis | None = None) -> int:
        """
        获取最小租金余额

        Args:
            redis: Redis客户端实例，如果为None则获取默认实例

        Returns:
            最小租金余额
        """
        redis = redis or RedisClient.get_instance()
        cached_value = await redis.get(cls.key)
        if cached_value is None:
            logger.warning("最小租金余额缓存未找到，正在更新...")
            min_balance_rent_cache = cls(redis)
            cached_value = await min_balance_rent_cache._gen_new_value()
            await redis.set(cls.key, cached_value, ex=timedelta(seconds=30))
        return int(cached_value)
