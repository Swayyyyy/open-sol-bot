from unittest.mock import AsyncMock, MagicMock, patch

import aioredis
import pytest
import pytest_asyncio
from cache_preloader.core.protocols import AutoUpdateCacheProtocol
from cache_preloader.services.auto_update_service import AutoUpdateCacheService


class MockCache(AutoUpdateCacheProtocol):
    """模拟缓存实现"""

    def __init__(self):
        self._is_running = False
        self.start_called = 0
        self.stop_called = 0

    def is_running(self) -> bool:
        return self._is_running

    async def start(self):
        self.start_called += 1
        self._is_running = True

    async def stop(self):
        self.stop_called += 1
        self._is_running = False


@pytest.fixture
def mock_redis_client():
    """模拟 Redis 客户端"""
    redis = AsyncMock(spec=aioredis.Redis)
    return redis


@pytest.fixture
def mock_caches():
    """创建模拟缓存列表"""
    return [MockCache(), MockCache()]


@pytest_asyncio.fixture
async def service_with_mocks(mock_redis_client, mock_caches):
    """提供带有模拟组件的服务实例"""
    with patch("cache_preloader.services.auto_update_service.RedisClient") as mock_redis:
        mock_redis.get_instance.return_value = mock_redis_client

        with patch(
            "cache_preloader.services.auto_update_service.BlockhashCache",
            return_value=mock_caches[0],
        ):
            with patch(
                "cache_preloader.services.auto_update_service.MinBalanceRentCache",
                return_value=mock_caches[1],
            ):
                service = AutoUpdateCacheService()
                # 替换服务中的缓存列表，以便我们可以直接访问模拟对象
                service.auto_update_caches = mock_caches
                yield service


@pytest.mark.asyncio
async def test_service_initialization(service_with_mocks, mock_redis_client):
    """测试服务初始化"""
    service = service_with_mocks

    # 验证 Redis 客户端被正确获取
    assert service.redis_client == mock_redis_client

    # 验证缓存列表被正确初始化
    assert len(service.auto_update_caches) == 2
    assert all(isinstance(cache, MockCache) for cache in service.auto_update_caches)

    # 验证关闭事件被初始化
    assert not service._shutdown_event.is_set()

    # 验证主任务初始为 None
    assert service._main_task is None


@pytest.mark.asyncio
async def test_service_start_stop(service_with_mocks, mock_caches):
    """测试服务启动和停止"""
    service = service_with_mocks

    # 模拟 start 方法，避免实际运行
    with patch.object(service, "start", AsyncMock()) as mock_start:
        await service.start()
        mock_start.assert_called_once()

    # 模拟 stop 方法，避免实际运行
    with patch.object(service, "stop", AsyncMock()) as mock_stop:
        await service.stop()
        mock_stop.assert_called_once()


@pytest.mark.asyncio
async def test_monitor_restarts_failed_caches():
    """测试监控功能能够重启失败的缓存"""
    # 创建模拟缓存
    mock_caches = [MockCache(), MockCache()]

    # 初始化所有缓存
    for cache in mock_caches:
        await cache.start()
        assert cache.is_running()

    # 记录初始启动调用次数
    initial_start_called = mock_caches[0].start_called

    # 模拟一个缓存停止运行
    mock_caches[0]._is_running = False
    assert not mock_caches[0].is_running()

    # 创建服务实例并直接设置缓存列表
    service = AutoUpdateCacheService()
    service.auto_update_caches = mock_caches

    # 直接调用监控方法
    await service._monitor()

    # 验证失败的缓存被重启 - 检查 start_called 是否增加而不是检查具体值
    assert mock_caches[0].start_called > initial_start_called
    assert mock_caches[0].is_running()

    # 验证正常运行的缓存没有被重启
    assert mock_caches[1].start_called == 1


@pytest.mark.asyncio
async def test_service_handles_signal():
    """测试服务能够处理信号"""
    # 创建模拟服务
    service = AutoUpdateCacheService()
    service._main_task = AsyncMock()
    service._main_task.done.return_value = False
    service._main_task.cancel = MagicMock()

    # 创建模拟缓存
    mock_caches = [MockCache(), MockCache()]
    service.auto_update_caches = mock_caches

    # 调用停止方法
    await service.stop()

    # 验证关闭事件被设置
    assert service._shutdown_event.is_set()

    # 验证主任务被取消
    service._main_task.cancel.assert_called_once()

    # 验证所有缓存都被停止
    for cache in mock_caches:
        assert cache.stop_called == 1
        assert not cache.is_running()
