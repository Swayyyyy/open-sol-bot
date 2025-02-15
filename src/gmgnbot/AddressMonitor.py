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
from collections import Counter


class AddressMonitor():
    def __init__(self):
        self.tasks: set[asyncio.Task] = set()
        self.store: NewTokenStore | None = None
        self.subscriber: NewTokenSubscriber | None = None
        self._shutdown_event = asyncio.Event()
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

    async def analysis_token(self, token_address):
        gmgn_monitor = GMGN()
        kline = gmgn_monitor.fetch_kline_data(token_address, datetime.datetime.now() - datetime.timedelta(hours=3), datetime.datetime.now(), "1m")
        kline['volume'] = kline['volume'].astype(float)
        start_time = kline.loc[kline['volume']>0]['time'].min()
        trade_info = gmgn_monitor.fetch_trader_data(token_address, start_time, 1000)
        buyer = trade_info.loc[trade_info['event']=='buy']['maker'].value_counts()
        buyer = buyer[buyer > 3]
        seller = trade_info.loc[trade_info['event']=='sell']['maker'].value_counts()
        seller = seller[seller > 3]
        either_operator = buyer.index.union(seller.index)
        opeartor_history = {}
        opeartor_history_str = {}
        for i in either_operator:
            opeartor_history[i] = gmgn_monitor.fetch_hoding(i)
            opeartor_history_str[i] = ','.join(opeartor_history[i]['token_address'].values[:10])
        history_count = Counter(opeartor_history_str.values())
        select_wallet = []
        for i in opeartor_history_str:
            if history_count[opeartor_history_str[i]] > 2:
                select_wallet.append(i)
        print(select_wallet)
    
async def main():
    monitor = AddressMonitor()
    await monitor.analysis_token("76TnEXcKjsEReBVzqF1AU5efRHacMzyFxGvquwZEpump")
        
        
if __name__ == "__main__":
    import asyncio
    # pre_start()
    asyncio.run(main())