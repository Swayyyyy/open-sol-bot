import asyncio
import signal

from gmgnbot.Data import GMGN, OKLine
from common.log import logger
from common.prestart import pre_start
from common.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from db.redis import RedisClient
from db.session import NEW_ASYNC_SESSION, provide_session
import time
import datetime
from collections import Counter
from dataclasses import dataclass
from common.models.tg_bot.monitor import Monitor as MonitorModel
from common.config import settings
from gmgnbot.constants import NEW_TOKEN_CHANNEL

from gmgnbot.monitor.monitor import MonitorService

monitor_service = MonitorService()

@dataclass
class Monitor:
    chat_id: int
    pk: int | None = None  # primary key
    target_wallet: str | None = None
    wallet_alias: str | None = None
    active: bool = True


class AddressMonitor():
    def __init__(self):
        self.tasks: set[asyncio.Task] = set()
        self._shutdown_event = asyncio.Event()
        self.OKLine = OKLine(settings.okline.channelAccessToken)
        self.tokens_history = {}
        self.redis = None

    async def start(self):
        """启动监控服务"""
        logger.info("Starting address monitor service...")
        self.redis = await RedisClient.get_instance()
        while True:
            try:
                data = await self.redis.brpop(NEW_TOKEN_CHANNEL, timeout=1)
                if data:
                    _, address = data
                    logger.info(f"New token address: {address}")
                    await self.analysis_token(address)
            except Exception as e:
                logger.error(f"Worker error: {e}")
                logger.exception(e)
                continue

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
        select_wallets = []
        for i in opeartor_history_str:
            if history_count[opeartor_history_str[i]] > 2:
                select_wallets.append(i)
        await self.AddToMonitor(select_wallets)

    async def AddToMonitor(self, target_wallets) -> None:
        """Add a new monitor to the database"""
        if target_wallets is None:
            raise ValueError("target_wallet is required")
        logger.info(f"Adding monitor for wallet: {target_wallets}")
        try:
            # 第一步：创建数据库记录
            monitors = [Monitor(
                chat_id=settings.tg_bot.manager_id,
                target_wallet=target_wallet,
                wallet_alias=None,
                active=True,
            ) for target_wallet in target_wallets]
            await monitor_service.addall(monitors)

        except Exception as e:
            raise ValueError(f"Failed to create monitor: {e}")
           
    
async def main():
    pre_start()
    monitor = AddressMonitor()
    await monitor.AddToMonitor(['9CPwN1YqWnLhgLUAQXNLxrPe8vQ1UpW7uLQgw45pqKEi', 'GbyNW641pn6QjdNooaAkHbSCihGogoBJdpPDZa1RZpQs'])

if __name__ == "__main__":
    asyncio.run(main())
    