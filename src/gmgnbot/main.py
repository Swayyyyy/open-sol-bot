import asyncio
import signal

from Data import GMGN, OKLine
from common.log import logger
from common.prestart import pre_start
from common.config import settings

from db.redis import RedisClient
from pump_monitor.new_token import NewTokenSubscriber
from pump_monitor.store import NewTokenStore
import time
import datetime


        
        
def main():
    monitor = GmgnMontior()
    return monitor.start()

if __name__ == "__main__":
    # pre_start()
    asyncio.run(main())
