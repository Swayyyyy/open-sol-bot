import asyncio
from unittest.mock import AsyncMock, patch

import aioredis
import pytest
import pytest_asyncio
from cache_preloader.caches.min_balance_rent import MinBalanceRentCache


@pytest.fixture
def mock_client():
    """模拟 Solana 客户端"""
    client = AsyncMock()
    return client


@pytest.fixture
def mock_redis():
    """模拟 Redis 客户端"""
    redis = AsyncMock(spec=aioredis.Redis)
    redis.set = AsyncMock()
    redis.get = AsyncMock(return_value=None)  # 初始时缓存为空
    return redis


@pytest.fixture
def mock_async_token():
    """模拟 AsyncToken 类"""
    with patch("cache_preloader.caches.min_balance_rent.AsyncToken") as mock:
        mock.get_min_balance_rent_for_exempt_for_account = AsyncMock(return_value=1000000)
        yield mock


@pytest_asyncio.fixture
async def cache_instance(mock_redis, mock_client, mock_async_token):
    """提供一个已初始化的缓存实例"""
    with patch(
        "cache_preloader.caches.min_balance_rent.get_async_client", return_value=mock_client
    ):
        cache = MinBalanceRentCache(mock_redis)
        await cache.start()
        try:
            yield cache
        finally:
            await cache.stop()


@pytest.mark.asyncio
async def test_gen_new_value(mock_redis, mock_client, mock_async_token):
    """测试生成新值的方法"""
    with patch(
        "cache_preloader.caches.min_balance_rent.get_async_client", return_value=mock_client
    ):
        cache = MinBalanceRentCache(mock_redis)
        value = await cache._gen_new_value()

        # 验证返回的是整数
        assert isinstance(value, int)
        assert value == 1000000

        # 验证调用了正确的方法
        mock_async_token.get_min_balance_rent_for_exempt_for_account.assert_called_once_with(
            mock_client
        )


@pytest.mark.asyncio
async def test_get_method_with_empty_cache(mock_redis, mock_client, mock_async_token):
    """测试 get 方法在缓存为空时的行为"""
    mock_redis.get.return_value = None

    with patch(
        "cache_preloader.caches.min_balance_rent.get_async_client", return_value=mock_client
    ):
        min_balance = await MinBalanceRentCache.get(mock_redis)

        # 验证返回值
        assert isinstance(min_balance, int)
        assert min_balance == 1000000

        # 验证缓存被设置
        mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_method_with_cached_value(mock_redis, mock_client, mock_async_token):
    """测试 get 方法在缓存有值时的行为"""
    # 模拟缓存中已有值
    mock_redis.get.return_value = b"2000000"

    with patch(
        "cache_preloader.caches.min_balance_rent.get_async_client", return_value=mock_client
    ):
        min_balance = await MinBalanceRentCache.get(mock_redis)

        # 验证返回值来自缓存
        assert isinstance(min_balance, int)
        assert min_balance == 2000000

        # 验证没有设置新的缓存
        mock_redis.set.assert_not_called()

        # 验证没有调用 AsyncToken
        mock_async_token.get_min_balance_rent_for_exempt_for_account.assert_not_called()


@pytest.mark.asyncio
async def test_auto_update_mechanism(cache_instance, mock_redis, mock_async_token):
    """测试自动更新机制"""
    # 等待更新发生
    await asyncio.sleep(1.5)

    # 验证缓存被更新
    mock_redis.set.assert_called()

    # 验证调用了 AsyncToken
    mock_async_token.get_min_balance_rent_for_exempt_for_account.assert_called()
