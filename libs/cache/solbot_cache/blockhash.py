import orjson as json
from solbot_common.utils.utils import get_async_client
from solbot_db.redis import RedisClient
from solders.hash import Hash  # type: ignore

from solbot_cache.constants import BLOCKHASH_CACHE_KEY


async def get_latest_blockhash_from_rpc() -> tuple[Hash, int]:
    resp = await get_async_client().get_latest_blockhash()
    return resp.value.blockhash, resp.value.last_valid_block_height


async def get_latest_blockhash() -> tuple[Hash, int]:
    """Get current blockhash and last valid block height from cache"""
    redis = RedisClient.get_instance()
    raw_cached_value = await redis.get(BLOCKHASH_CACHE_KEY)
    if raw_cached_value is None:
        return await get_latest_blockhash_from_rpc()
    cached_value = json.loads(raw_cached_value)
    return Hash.from_string(cached_value["blockhash"]), int(cached_value["last_valid_block_height"])
