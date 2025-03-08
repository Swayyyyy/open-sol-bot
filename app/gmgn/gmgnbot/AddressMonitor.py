import asyncio
import datetime
import signal
import time
from collections import Counter
from dataclasses import dataclass
from typing import ParamSpec, TypedDict, TypeVar, cast

from gmgnbot.constants import NEW_TOKEN_CHANNEL
from gmgnbot.Data import GMGN, OKLine
from gmgnbot.monitor.copytrade import CopyTradeService
from gmgnbot.monitor.monitor import MonitorService
from solbot_common.config import settings
from solbot_common.log import logger
from solbot_common.models.tg_bot.monitor import Monitor as MonitorModel
from solbot_common.models.tg_bot.user import User
from solbot_common.prestart import pre_start
from solbot_db.redis import RedisClient
from solbot_db.session import NEW_ASYNC_SESSION, provide_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select



@dataclass
class CopyTrade:
    owner: str
    chat_id: int
    pk: int | None = None  # primary key
    target_wallet: str | None = None
    wallet_alias: str | None = None
    is_fixed_buy: bool = True
    fixed_buy_amount: float = 0.5
    auto_follow: bool = True
    stop_loss: bool = False
    no_sell: bool = False
    priority: float = 0.002
    anti_sandwich: bool = False
    auto_slippage: bool = True
    custom_slippage: float = 10  # 0-100%
    active: bool = True


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
        self.monitor_service = MonitorService()
        self.copy_trade_service = CopyTradeService()

        
    async def start(self):
        """启动监控服务"""
        logger.info("Starting address monitor service...")
        self.redis = await RedisClient.get_instance()
        self.pop_script = self.redis.register_script("""
        local res = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
        if res[1] and tonumber(res[2]) <= tonumber(ARGV[1]) then
            redis.call('ZREM', KEYS[1], res[1])
            return res[1]
        end
        return nil
        """)
        while True:
            try:
                current_time = time.time()
                result = await self.redis.eval(self.pop_script, 1, NEW_TOKEN_CHANNEL, current_time)
                if result:
                    # 如果 redis 连接使用的是 decode_responses=False 则返回的是 bytes 类型
                    address = result.decode()
                # data = await self.redis.brpop(NEW_TOKEN_CHANNEL, timeout=1)
                # if data:
                #     _, address = data
                    logger.info(f"New token address: {address}")
                    await self.analysis_token(address)
            except Exception as e:
                logger.error(f"Worker error: {e}")
                logger.exception(e)
                continue

    async def analysis_token(self, token_address):
        gmgn_monitor = GMGN()
        kline = gmgn_monitor.fetch_kline_data(
            token_address,
            datetime.datetime.now() - datetime.timedelta(hours=3),
            datetime.datetime.now(), "1m")
        kline['volume'] = kline['volume'].astype(float)
        start_time = kline.loc[kline['volume'] > 0]['time'].min()
        trade_info = gmgn_monitor.fetch_trader_data(token_address, start_time,
                                                    1000)
        buyer = trade_info.loc[trade_info['event'] ==
                               'buy']['maker'].value_counts()
        buyer = buyer[buyer > 3]
        seller = trade_info.loc[trade_info['event'] ==
                                'sell']['maker'].value_counts()
        seller = seller[seller > 3]
        either_operator = buyer.index.union(seller.index)
        opeartor_history = {}
        opeartor_history_str = {}
        for i in either_operator:
            opeartor_history[i] = gmgn_monitor.fetch_hoding(i)
            opeartor_history_str[i] = ','.join(
                opeartor_history[i]['token_address'].values[:10])
        history_count = Counter(opeartor_history_str.values())
        select_wallets = []
        for i in opeartor_history_str:
            if history_count[opeartor_history_str[i]] > 5:
                select_wallets.append(i)
        if len(select_wallets) < 5:
            return
        await self.AddToMonitor(select_wallets)

    async def AddToMonitor(self, target_wallets,retry=0) -> None:
        if retry > 3:
            raise ValueError("Failed to create monitor after 3 retries")
        """Add a new monitor to the database"""
        if target_wallets is None:
            raise ValueError("target_wallet is required")
        logger.info(f"Adding monitor for wallet: {target_wallets}")
        try:
            pbkey = await self.copy_trade_service.getpk(settings.tg_bot.manager_id)
            if not pbkey:
                raise ValueError("Wallet not found")
            # stmt = select(User.pubkey).where(User.chat_id == settings.tg_bot.manager_id).limit(1)
            # public_key = (await NEW_ASYNC_SESSION.execute(stmt)).scalar_one_or_none()
            monitors = [
                CopyTrade(
                    owner=pbkey,
                    chat_id=settings.tg_bot.manager_id,
                    target_wallet=target_wallet,
                    wallet_alias=None,
                    active=True,
                ) for target_wallet in target_wallets
            ]
            await self.copy_trade_service.addall(monitors)

        except Exception as e:
            await self.AddToMonitor(target_wallets, retry + 1)
            logger.error(f"Failed to create monitor: {e}")
            


async def main():
    pre_start()
    monitor = AddressMonitor()
    await monitor.AddToMonitor([
        'G7ZXGygKPS2vts5eZ6ws8sXPVdqr1VBKhiVBz6qmShbN',
        'Db43M7vneandhvPW2kwn92dZEBA1pdubQ6FMGJAFWZUF',
        'Hn5HkzBp2TXJ1CpL22kXjmveKT3DcoUZ6nPnQZcJX9DU',
        'HsJN2ESiwGaAcwhgS8vqJLYb7DnnYdb1RTS1j5hTePcz',
    ])


if __name__ == "__main__":
    asyncio.run(main())
