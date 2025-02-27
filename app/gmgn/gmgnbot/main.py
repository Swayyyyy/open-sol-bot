import asyncio
import signal

from gmgnbot.Data import GMGN, OKLine
from common.log import logger
from common.prestart import pre_start
from common.config import settings

from db.redis import RedisClient
import time
import datetime

from gmgnbot.AddressMonitor import AddressMonitor
from gmgnbot.TokenMontior import GmgnMontior


async def main():
    gmgnMonitor = GmgnMontior()
    addMonitor = AddressMonitor()
    await asyncio.gather(gmgnMonitor.start(), addMonitor.start())
    
if __name__ == "__main__":
    pre_start()
    asyncio.run(main())
