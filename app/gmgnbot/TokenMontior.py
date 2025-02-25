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
from constants import NEW_TOKEN_QUEUE_KEY, NEW_TOKEN_CHANNEL

class GmgnMontior:
    def __init__(self):
        self.tasks: set[asyncio.Task] = set()
        self.store: NewTokenStore | None = None
        self.subscriber: NewTokenSubscriber | None = None
        self._shutdown_event = asyncio.Event()
        self.gmgn_monitor = GMGN()
        self.OKLine = OKLine(settings.okline.channelAccessToken)
        self.redis = None
        
    async def start(self):
        """启动监控服务"""
        logger.info("Starting pump monitor service...")
        self.redis = await RedisClient.get_instance()
        await self.monitor_token()

        # 等待关闭信号
        await self._shutdown_event.wait()

    async def monitor_token(self):
        while True:
            try:
                new_token_info = self.gmgn_monitor.fetch_hot_token()
                tokens = new_token_info.loc[new_token_info['price_change_percent1h'] > 1000][['holder_count', 'address']]
                for i in tokens['address']:
                    result = await self.redis.sadd(NEW_TOKEN_QUEUE_KEY, i)
                    if result:
                        logger.info(f'add new token: {i}')
                        await self.redis.lpush(NEW_TOKEN_CHANNEL, i)
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error processing item: {e}")
    