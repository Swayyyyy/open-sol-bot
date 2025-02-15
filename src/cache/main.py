import asyncio
import signal
from typing import List

from cache.auto.base import AutoUpdateCacheProtocol
from cache.auto.blockhash import BlockhashCache
from cache.auto.min_balance_rent import MinBalanceRentCache
from cache.auto.raydium_pool import RaydiumPoolCache
from common.config import settings
from common.log import logger
from common.prestart import pre_start
from db.redis import RedisClient


class AutoUpdateCacheService:
    """自动更新缓存服务"""

    def __init__(self):
        self.redis_client = RedisClient.get_instance()
        self.auto_update_caches: List[AutoUpdateCacheProtocol] = [
            BlockhashCache(self.redis_client),
            MinBalanceRentCache(self.redis_client),
            # RaydiumPoolCache(settings.rpc.rpc_url, self.redis_client, 20),
        ]
        self._shutdown_event = asyncio.Event()
        self._main_task = None

    async def start(self):
        """启动缓存服务"""
        try:
            logger.info("Starting auto-update cache service...")
            # 启动所有缓存服务
            await asyncio.gather(*[cache.start() for cache in self.auto_update_caches])

            # 创建主监控任务
            self._main_task = asyncio.create_task(self._monitor())
            # 等待关闭信号
            await self._shutdown_event.wait()

        except asyncio.CancelledError:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.exception(f"Error in cache service: {e}")
        finally:
            await self.stop()

    async def _monitor(self):
        """监控所有缓存服务的状态"""
        try:
            while not self._shutdown_event.is_set():
                # 检查所有缓存是否正常运行
                for cache in self.auto_update_caches:
                    if not cache.is_running():
                        logger.warning(
                            f"{cache.__class__.__name__} is not running, restarting..."
                        )
                        await cache.start()
                # 每分钟检查一次
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            pass

    async def stop(self):
        """停止缓存服务"""
        logger.info("Stopping auto-update cache service...")

        # 设置关闭信号
        self._shutdown_event.set()

        # 取消主监控任务
        if self._main_task and not self._main_task.done():
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass

        # 停止所有缓存服务
        await asyncio.gather(
            *[cache.stop() for cache in self.auto_update_caches], return_exceptions=True
        )

        # 记录停止日志
        for cache in self.auto_update_caches:
            logger.info(f"Stopped {cache.__class__.__name__}")


async def main():
    """主函数"""
    pre_start()

    service = AutoUpdateCacheService()

    def signal_handler():
        """信号处理函数"""
        logger.info("Received shutdown signal")
        # 使用 create_task 来避免阻塞信号处理
        asyncio.create_task(service.stop())

    # 注册信号处理
    loop = asyncio.get_running_loop()

    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)

        # 启动服务并等待结束
        await service.start()
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise
    finally:
        # 移除信号处理器
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(sig)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
