import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional, Protocol

import aioredis

from common.log import logger


class AutoUpdateCacheProtocol(Protocol):
    def is_running(self) -> bool: ...
    async def start(self): ...
    async def stop(self): ...


class BaseAutoUpdateCache(AutoUpdateCacheProtocol):
    """Base class for all cache managers"""

    key: str
    update_interval: int = 30

    def __init__(self, redis: aioredis.Redis, update_interval: int = 30):
        """
        Args:
            update_interval: Seconds between cache updates
        """
        self.redis = redis
        self._update_interval = update_interval
        self._last_update: Optional[datetime] = None
        self._update_task: Optional[asyncio.Task] = None
        self._is_running = False

    def is_running(self) -> bool:
        return self._is_running

    async def start(self):
        """Start the automatic update task"""
        if self._is_running:
            return
        self._is_running = True
        self._update_task = asyncio.create_task(self._auto_update())
        logger.info(f"{self.__class__.__name__} cache manager started")

    async def stop(self):
        """Stop the automatic update task"""
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
        logger.info(f"{self.__class__.__name__} cache manager stopped")

    async def _auto_update(self):
        """Automatic update task"""
        while self._is_running:
            try:
                val = await self._gen_new_value()
                await self.redis.set(
                    self.key, val, ex=timedelta(seconds=self._update_interval)
                )
                logger.info(f"Updated {self.__class__.__name__} cachei, value: {val}")
                self._last_update = datetime.now()
                await asyncio.sleep(self._update_interval - 1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating cache in {self.__class__.__name__}: {e}")
                await asyncio.sleep(1)  # Short delay before retry on error

    async def _gen_new_value(self) -> Any:
        """Generate a new value"""
        raise NotImplementedError

    @property
    def last_update(self) -> Optional[datetime]:
        """Get the last update time"""
        return self._last_update

    def __del__(self):
        """Ensure the update task is stopped when the object is deleted"""
        if self._is_running:
            asyncio.create_task(self.stop())
