import asyncio
import signal

from common.log import logger
from common.prestart import pre_start

from db.redis import RedisClient
from pump_monitor.new_token import NewTokenSubscriber
from pump_monitor.store import NewTokenStore


class PumpMonitor:
    def __init__(self):
        self.tasks: set[asyncio.Task] = set()
        self.store: NewTokenStore | None = None
        self.subscriber: NewTokenSubscriber | None = None
        self._shutdown_event = asyncio.Event()

    async def start(self):
        """启动监控服务"""
        logger.info("Starting pump monitor service...")
        redis = await RedisClient.get_instance()

        # 初始化组件
        self.store = NewTokenStore(redis)
        self.subscriber = NewTokenSubscriber(redis)

        # 创建并跟踪任务
        store_task = asyncio.create_task(self.store.start())
        # subscriber_task = asyncio.create_task(self.subscriber.start())

        self.tasks.update({store_task})
        logger.info("Pump monitor service started")

        # 等待关闭信号
        await self._shutdown_event.wait()

    async def shutdown(self):
        """关闭服务"""
        logger.info("Shutting down pump monitor service...")

        # 停止组件
        if self.subscriber:
            await self.subscriber.stop()
        if self.store:
            await self.store.stop()

        # 取消所有任务
        for task in self.tasks:
            task.cancel()

        # 等待所有任务完成
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        self.tasks.clear()
        logger.info("Pump monitor service stopped")

    def signal_shutdown(self):
        """触发关闭信号"""
        self._shutdown_event.set()


async def main():
    # 创建监控服务
    monitor = PumpMonitor()

    # 设置信号处理
    def handle_signal(sig):
        logger.info(f"Received signal {sig}")
        monitor.signal_shutdown()

    # 注册信号处理器
    for sig in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_event_loop().add_signal_handler(sig, lambda s=sig: handle_signal(s))

    try:
        await monitor.start()
    finally:
        await monitor.shutdown()


if __name__ == "__main__":
    pre_start()
    asyncio.run(main())
