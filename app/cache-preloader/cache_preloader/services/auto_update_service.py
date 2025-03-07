import asyncio

from solbot_common.log import logger
from solbot_db.redis import RedisClient

from cache_preloader.caches.blockhash import BlockhashCache
from cache_preloader.caches.min_balance_rent import MinBalanceRentCache
from cache_preloader.core.protocols import AutoUpdateCacheProtocol


class AutoUpdateCacheService:
    """自动更新缓存服务"""

    def __init__(self):
        self.redis_client = RedisClient.get_instance()
        self.auto_update_caches: list[AutoUpdateCacheProtocol] = [
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
                        logger.warning(f"{cache.__class__.__name__} is not running, restarting...")
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
