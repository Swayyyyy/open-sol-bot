from datetime import timedelta

import aioredis
import orjson as json
from solbot_cache.constants import BLOCKHASH_CACHE_KEY
from solbot_common.log import logger
from solbot_common.utils import get_async_client
from solbot_db.redis import RedisClient
from solders.hash import Hash  # type: ignore

from cache_preloader.core.base import BaseAutoUpdateCache


class BlockhashCache(BaseAutoUpdateCache):
    """区块哈希缓存管理器"""

    key = BLOCKHASH_CACHE_KEY

    def __init__(self, redis: aioredis.Redis):
        """
        初始化区块哈希缓存管理器

        Args:
            redis: Redis客户端实例
        """
        self.client = get_async_client()
        self.redis = redis
        super().__init__(redis)

    @classmethod
    async def _get_latest_blockhash(cls) -> tuple[Hash, int]:
        """
        获取最新的区块哈希

        Returns:
            区块哈希和最后有效区块高度的元组
        """
        resp = await get_async_client().get_latest_blockhash()
        return resp.value.blockhash, resp.value.last_valid_block_height

    async def _gen_new_value(self) -> str:
        """
        生成新的缓存值

        Returns:
            序列化后的区块哈希信息
        """
        _hash, _last_valid_block_height = await self._get_latest_blockhash()
        return json.dumps(
            {
                "blockhash": str(_hash),
                "last_valid_block_height": str(_last_valid_block_height),
            }
        ).decode("utf-8")

    @classmethod
    async def get(cls, redis: aioredis.Redis | None = None) -> tuple[Hash, int]:
        """
        获取当前区块哈希和最后有效区块高度
        如果可用，使用缓存值

        Args:
            redis: Redis客户端实例，如果为None则获取默认实例

        Returns:
            区块哈希和最后有效区块高度的元组
        """
        # if os.getenv("PYTEST_CURRENT_TEST"):
        # return await cls._get_latest_blockhash()

        redis = redis or RedisClient.get_instance()
        raw_cached_value = await redis.get(cls.key)
        if raw_cached_value is None:
            logger.warning("区块哈希缓存未找到，正在更新...")
            blockhash_cache = cls(redis)
            raw_cached_value = await blockhash_cache._gen_new_value()
            await redis.set(cls.key, raw_cached_value, ex=timedelta(seconds=30))
        cached_value = json.loads(raw_cached_value)
        return Hash.from_string(cached_value["blockhash"]), int(
            cached_value["last_valid_block_height"]
        )
