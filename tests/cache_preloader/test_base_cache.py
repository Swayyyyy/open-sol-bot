import asyncio
from unittest.mock import AsyncMock

import aioredis
import pytest
import pytest_asyncio
from cache_preloader.core.base import BaseAutoUpdateCache


class TestCache(BaseAutoUpdateCache):
    """测试用缓存类"""

    key = "test_cache_key"

    def __init__(self, redis, update_interval=1):
        self.gen_value_called = 0
        self.gen_value_result = "test_value"
        super().__init__(redis, update_interval)

    async def _gen_new_value(self):
        self.gen_value_called += 1
        return self.gen_value_result


@pytest.fixture
def mock_redis():
    """模拟 Redis 客户端"""
    redis = AsyncMock(spec=aioredis.Redis)
    redis.set = AsyncMock()
    redis.get = AsyncMock(return_value="cached_value")
    return redis


@pytest_asyncio.fixture
async def cache_instance(mock_redis):
    """提供一个已初始化的缓存实例"""
    cache = TestCache(mock_redis, update_interval=1)
    yield cache


@pytest.mark.asyncio
async def test_start_stop(cache_instance):
    """测试缓存启动和停止"""
    assert not cache_instance.is_running()

    # 启动缓存
    await cache_instance.start()
    assert cache_instance.is_running()

    # 停止缓存
    await cache_instance.stop()
    assert not cache_instance.is_running()


@pytest.mark.asyncio
async def test_auto_update(cache_instance):
    """测试自动更新机制"""
    await cache_instance.start()

    try:
        # 等待更新发生
        await asyncio.sleep(1.5)

        # 验证更新被调用
        assert cache_instance.gen_value_called >= 1
        cache_instance.redis.set.assert_called()
    finally:
        await cache_instance.stop()


@pytest.mark.asyncio
async def test_update_interval(mock_redis):
    """测试不同的更新间隔"""
    # 创建一个更长间隔的缓存
    cache = TestCache(mock_redis, update_interval=2)
    await cache.start()

    try:
        # 等待短于间隔的时间
        await asyncio.sleep(1)
        initial_calls = cache.gen_value_called

        # 等待足够长的时间让更新发生
        await asyncio.sleep(1.5)
        assert cache.gen_value_called > initial_calls
    finally:
        await cache.stop()


@pytest.mark.asyncio
async def test_error_handling(mock_redis):
    """测试错误处理"""
    cache = TestCache(mock_redis)

    # 模拟生成值时出错
    async def raise_error():
        raise Exception("Test error")

    cache._gen_new_value = raise_error

    await cache.start()
    try:
        # 等待错误处理
        await asyncio.sleep(1.5)
        # 应该继续运行，不会崩溃
        assert cache.is_running()
    finally:
        await cache.stop()


@pytest.mark.asyncio
async def test_last_update_property(cache_instance):
    """测试最后更新时间属性"""
    assert cache_instance.last_update is None

    await cache_instance.start()
    try:
        await asyncio.sleep(1.5)
        assert cache_instance.last_update is not None
    finally:
        await cache_instance.stop()
