import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aioredis
import orjson as json
import pytest
import pytest_asyncio
from cache_preloader.caches.blockhash import BlockhashCache
from solders.hash import Hash


@pytest.fixture
def mock_client():
    """模拟 Solana 客户端"""
    client = AsyncMock()
    # 创建一个模拟的 blockhash 响应
    mock_response = MagicMock()
    mock_response.value.blockhash = Hash.default()  # 使用默认的 Hash 对象
    mock_response.value.last_valid_block_height = 100
    client.get_latest_blockhash.return_value = mock_response
    return client


@pytest.fixture
def mock_redis():
    """模拟 Redis 客户端"""
    redis = AsyncMock(spec=aioredis.Redis)
    redis.set = AsyncMock()
    redis.get = AsyncMock(return_value=None)  # 初始时缓存为空
    return redis


@pytest_asyncio.fixture
async def cache_instance(mock_redis, mock_client):
    """提供一个已初始化的缓存实例"""
    with patch("cache_preloader.caches.blockhash.get_async_client", return_value=mock_client):
        cache = BlockhashCache(mock_redis)
        await cache.start()
        try:
            yield cache
        finally:
            await cache.stop()


@pytest.mark.asyncio
async def test_gen_new_value(mock_redis, mock_client):
    """测试生成新值的方法"""
    with patch("cache_preloader.caches.blockhash.get_async_client", return_value=mock_client):
        cache = BlockhashCache(mock_redis)
        value = await cache._gen_new_value()

        # 验证返回的是 JSON 字符串
        assert isinstance(value, str)

        # 解析 JSON 并验证内容
        data = json.loads(value)
        assert "blockhash" in data
        assert "last_valid_block_height" in data
        assert data["last_valid_block_height"] == "100"


@pytest.mark.asyncio
async def test_get_method_with_empty_cache(mock_redis, mock_client):
    """测试 get 方法在缓存为空时的行为"""
    mock_redis.get.return_value = None

    with patch("cache_preloader.caches.blockhash.get_async_client", return_value=mock_client):
        blockhash, last_valid = await BlockhashCache.get(mock_redis)

        # 验证返回值类型
        assert isinstance(blockhash, Hash)
        assert isinstance(last_valid, int)
        assert last_valid == 100

        # 验证缓存被设置
        mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_method_with_cached_value(mock_redis, mock_client):
    """测试 get 方法在缓存有值时的行为"""
    # 模拟缓存中已有值
    cached_value = json.dumps(
        {"blockhash": str(Hash.default()), "last_valid_block_height": "200"}
    ).decode("utf-8")
    mock_redis.get.return_value = cached_value

    with patch("cache_preloader.caches.blockhash.get_async_client", return_value=mock_client):
        blockhash, last_valid = await BlockhashCache.get(mock_redis)

        # 验证返回值来自缓存
        assert isinstance(blockhash, Hash)
        assert isinstance(last_valid, int)
        assert last_valid == 200

        # 验证没有设置新的缓存
        mock_redis.set.assert_not_called()


@pytest.mark.asyncio
async def test_auto_update_mechanism(cache_instance, mock_redis):
    """测试自动更新机制"""
    # 等待更新发生
    await asyncio.sleep(1.5)

    # 验证缓存被更新
    mock_redis.set.assert_called()
