from typing import Protocol


class AutoUpdateCacheProtocol(Protocol):
    """自动更新缓存协议"""

    def is_running(self) -> bool:
        """检查缓存服务是否正在运行"""
        ...

    async def start(self):
        """启动缓存服务"""
        ...

    async def stop(self):
        """停止缓存服务"""
        ...
