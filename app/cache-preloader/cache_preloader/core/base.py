import asyncio
from datetime import datetime, timedelta
from typing import Any

import aioredis
from solbot_common.log import logger

from cache_preloader.core.protocols import AutoUpdateCacheProtocol


class BaseAutoUpdateCache(AutoUpdateCacheProtocol):
    """所有缓存管理器的基类"""

    key: str
    update_interval: int = 30

    def __init__(self, redis: aioredis.Redis, update_interval: int = 30):
        """
        Args:
            redis: Redis客户端实例
            update_interval: 缓存更新间隔（秒）
        """
        self.redis = redis
        self._update_interval = update_interval
        self._last_update: datetime | None = None
        self._update_task: asyncio.Task | None = None
        self._is_running = False

    def is_running(self) -> bool:
        """检查缓存服务是否正在运行"""
        return self._is_running

    async def start(self):
        """启动自动更新任务"""
        if self._is_running:
            return
        self._is_running = True
        self._update_task = asyncio.create_task(self._auto_update())
        logger.info(f"{self.__class__.__name__} 缓存管理器已启动")

    async def stop(self):
        """停止自动更新任务"""
        if not self._is_running:
            return
        self._is_running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None
        logger.info(f"{self.__class__.__name__} 缓存管理器已停止")

    async def _auto_update(self):
        """自动更新任务"""
        while self._is_running:
            try:
                val = await self._gen_new_value()
                await self.redis.set(self.key, val, ex=timedelta(seconds=self._update_interval))
                logger.info(f"已更新 {self.__class__.__name__} 缓存，值: {val}")
                self._last_update = datetime.now()
                await asyncio.sleep(self._update_interval - 1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"{self.__class__.__name__} 更新缓存时出错: {e}")
                await asyncio.sleep(1)  # 出错后短暂延迟再重试

    async def _gen_new_value(self) -> Any:
        """生成新的缓存值"""
        raise NotImplementedError

    @property
    def last_update(self) -> datetime | None:
        """获取最后更新时间"""
        return self._last_update

    def __del__(self):
        """确保对象被删除时停止更新任务"""
        if self._is_running:
            # TODO: 需要采用更优雅的方式停止
            return asyncio.create_task(self.stop())
