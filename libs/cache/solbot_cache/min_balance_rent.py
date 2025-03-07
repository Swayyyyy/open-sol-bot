from solbot_common.utils.utils import get_async_client
from solbot_db.redis import RedisClient
from spl.token.async_client import AsyncToken

from solbot_cache.constants import MIN_BALANCE_RENT_CACHE_KEY


async def get_min_balance_rent_from_rpc() -> int:
    """Get current min balance rent from RPC"""
    client = get_async_client()
    min_balance = await AsyncToken.get_min_balance_rent_for_exempt_for_account(client)
    return min_balance


async def get_min_balance_rent() -> int:
    """Get current min balance rent from cache"""
    redis = RedisClient.get_instance()
    cached_value = await redis.get(MIN_BALANCE_RENT_CACHE_KEY)
    if cached_value is None:
        return await get_min_balance_rent_from_rpc()
    return int(cached_value)
