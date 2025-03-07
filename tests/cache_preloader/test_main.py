import asyncio
import signal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cache_preloader.main import main


@pytest.mark.asyncio
async def test_main_function():
    """测试主函数"""
    # 模拟 AutoUpdateCacheService
    mock_service = AsyncMock()
    mock_service.start = AsyncMock()
    mock_service.stop = AsyncMock()

    # 模拟 pre_start 函数
    mock_pre_start = MagicMock()

    # 模拟信号处理
    mock_loop = AsyncMock()
    mock_loop.add_signal_handler = MagicMock()
    mock_loop.remove_signal_handler = MagicMock()

    with patch("cache_preloader.main.pre_start", mock_pre_start):
        with patch("cache_preloader.main.AutoUpdateCacheService", return_value=mock_service):
            with patch("asyncio.get_running_loop", return_value=mock_loop):
                # 运行主函数
                await main()

    # 验证调用
    mock_pre_start.assert_called_once()
    mock_service.start.assert_called_once()

    # 验证信号处理器被添加
    assert mock_loop.add_signal_handler.call_count == 2
    mock_loop.add_signal_handler.assert_any_call(
        signal.SIGTERM, mock_loop.add_signal_handler.call_args_list[0][0][1]
    )
    mock_loop.add_signal_handler.assert_any_call(
        signal.SIGINT, mock_loop.add_signal_handler.call_args_list[1][0][1]
    )

    # 验证信号处理器被移除
    assert mock_loop.remove_signal_handler.call_count == 2
    mock_loop.remove_signal_handler.assert_any_call(signal.SIGTERM)
    mock_loop.remove_signal_handler.assert_any_call(signal.SIGINT)


@pytest.mark.asyncio
async def test_main_function_with_exception():
    """测试主函数异常处理"""
    # 模拟 AutoUpdateCacheService
    mock_service = AsyncMock()
    mock_service.start = AsyncMock(side_effect=Exception("Test exception"))

    # 模拟 pre_start 函数
    mock_pre_start = MagicMock()

    # 模拟信号处理
    mock_loop = AsyncMock()
    mock_loop.add_signal_handler = MagicMock()
    mock_loop.remove_signal_handler = MagicMock()

    with patch("cache_preloader.main.pre_start", mock_pre_start):
        with patch("cache_preloader.main.AutoUpdateCacheService", return_value=mock_service):
            with patch("asyncio.get_running_loop", return_value=mock_loop):
                # 运行主函数，应该抛出异常
                with pytest.raises(Exception, match="Test exception"):
                    await main()

    # 验证调用
    mock_pre_start.assert_called_once()
    mock_service.start.assert_called_once()

    # 验证信号处理器被添加
    assert mock_loop.add_signal_handler.call_count == 2

    # 验证信号处理器被移除（即使发生异常）
    assert mock_loop.remove_signal_handler.call_count == 2


@pytest.mark.asyncio
async def test_signal_handler():
    """测试信号处理函数"""
    # 模拟 AutoUpdateCacheService
    mock_service = AsyncMock()
    mock_service.stop = AsyncMock()

    # 模拟 create_task
    mock_create_task = MagicMock()

    with patch("asyncio.create_task", mock_create_task):
        # 创建主函数的局部变量
        with patch("cache_preloader.main.AutoUpdateCacheService", return_value=mock_service):
            with patch("asyncio.get_running_loop", return_value=AsyncMock()):
                # 运行主函数，但立即中断
                main_task = asyncio.create_task(main())
                await asyncio.sleep(0.1)
                main_task.cancel()

                try:
                    await main_task
                except asyncio.CancelledError:
                    pass

    # 由于我们无法直接访问信号处理函数，这个测试主要是确保主函数能够正常运行
    # 实际的信号处理逻辑测试需要更复杂的设置
