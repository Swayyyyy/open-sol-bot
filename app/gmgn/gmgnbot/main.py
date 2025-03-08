import asyncio
import signal

from aioredis import Redis
from gmgnbot.Data import GMGN, OKLine
from solbot_common.log import logger
from solbot_common.prestart import pre_start
from solbot_common.config import settings

from solbot_db.redis import RedisClient
import time
import datetime
from multiprocessing import Process

from gmgnbot.AddressMonitor import AddressMonitor
from gmgnbot.TokenMontior import GmgnMontior

def new_redis_instance() -> Redis:
    return Redis.from_url(
        str(settings.db.redis), encoding="utf-8", decode_responses=True
    )

class gmgnBot:
    def __init__(self):
        # 分别创建两个 Redis 实例
        self.gmgnMonitor = GmgnMontior(redis_client=new_redis_instance())
        self.addMonitor = AddressMonitor(redis_client=new_redis_instance())
    
    async def start(self):
        await asyncio.gather(
            self.gmgnMonitor.start(),
            self.addMonitor.start()
        )

def run_gmgn():
    # 为 gmgnMonitor 启动单独进程
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = gmgnBot()  # 或者单独构造 gmgnMonitor
    loop.run_until_complete(bot.gmgnMonitor.start())

def run_addmon():
    # 为 addMonitor 启动单独进程
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = gmgnBot()  # 或者单独构造 addMonitor
    loop.run_until_complete(bot.addMonitor.start())
    
async def main():
    # 如果只想并行跑两个进程，可以这样：
    p1 = Process(target=run_gmgn)
    p2 = Process(target=run_addmon)
    p1.start()
    p2.start()
    p1.join()
    p2.join()

if __name__ == "__main__":
    pre_start()
    asyncio.run(main())