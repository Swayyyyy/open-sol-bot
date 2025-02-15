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


class GmgnMontior:
    def __init__(self):
        self.tasks: set[asyncio.Task] = set()
        self.store: NewTokenStore | None = None
        self.subscriber: NewTokenSubscriber | None = None
        self._shutdown_event = asyncio.Event()
        self.gmgn_monitor = GMGN()
        self.OKLine = OKLine(settings.okline.channelAccessToken)
        self.tokens_history = {}

    async def start(self):
        """启动监控服务"""
        logger.info("Starting pump monitor service...")
        redis = await RedisClient.get_instance()

        # 初始化组件
        self.store = NewTokenStore(redis)
        # 创建并跟踪任务
        await self.monitor_token()

        # 等待关闭信号
        await self._shutdown_event.wait()

    async def monitor_token(self):
        while True:
            try:
                new_token_info = self.gmgn_monitor.fetch_hot_token()
                tokens = new_token_info.loc[new_token_info['price_change_percent1h'] > 1000][['holder_count', 'address']]
                for i in tokens.index:
                    self.tokens_history[tokens.loc[i, 'address']] = max(tokens.loc[i, 'holder_count'], self.tokens_history.get(tokens.loc[i, 'address'], 0))
                print(self.tokens_history)
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error processing item: {e}")
    
    async def analysis_token(self, token):
        kline = self.gmgn_monitor.fetch_kline_data(token, datetime.datetime.now(), datetime.datetime.now() - datetime.timedelta(days=1), "1m")
        