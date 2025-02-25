import asyncio
from collections.abc import Sequence

from common.config import settings
from common.log import logger
from common.prestart import pre_start
from common.types import copytrade
from common.utils import get_async_client
from db.redis import RedisClient
from solders.pubkey import Pubkey  # type: ignore
from wallet_tracker.benchmark import BenchmarkService
from wallet_tracker.tx_monitor import TxMonitor
from wallet_tracker.tx_worker import TransactionWorker


class WalletTracker:
    def __init__(self, init_wallets: Sequence[Pubkey]):
        self.redis = RedisClient.get_instance()
        self.client = get_async_client()
        self.wallets = init_wallets
        self.transaction_monitor = TxMonitor(self.wallets, mode=settings.monitor.mode)
        self.transaction_worker = TransactionWorker(self.redis)
        self.benchmark_service = BenchmarkService()

    # @provide_session
    # async def sync_wallet(self, *, session: AsyncSession = NEW_ASYNC_SESSION):
    #     """
    #     The
    #     function `sync_wallet` iterates through wallets, retrieves tokens, and updates associated
    #     token accounts in a database session.
    #     """
    #     tokens = []
    #     mint_accounts = {}
    #     for wallet in self.wallets:
    #         _tokens = await get_wallet_tokens(wallet, self.client)
    #         tokens.extend(_tokens)
    #
    #     # 不存在则插入，存在则更新
    #     for token in tokens:
    #         mint_account = mint_accounts.get(token.mint.__str__())
    #         if mint_account is None:
    #             mint_account = await get_mint_account(token.mint, self.client)
    #             mint_accounts[token.mint.__str__()] = mint_account
    #         if mint_account is None:
    #             continue
    #         ata = AssociatedTokenAccount.from_token_account(
    #             token, mint_account.decimals
    #         )
    #         await session.merge(ata)
    #         logger.info(f"sync wallet {wallet} token {token.mint} ata {ata}")
    #     await session.commit()
    #     logger.info("sync wallet done")

    async def start(self):
        # await self.sync_wallet()
        # 使用 asyncio.gather 并发执行监控任务

        await asyncio.gather(
            self.benchmark_service.start(),
            self.transaction_monitor.start(),
            self.transaction_worker.start(),
        )

    async def stop(self):
        await self.transaction_monitor.stop()
        await self.transaction_worker.stop()
        await self.benchmark_service.stop()


if __name__ == "__main__":
    pre_start()

    # 从配置中获取被监听钱包
    wallets = set(settings.monitor.wallets)

    # 从跟单配置中获取需要被监听的钱包
    for copytrade in settings.copytrades:
        wallets.add(copytrade.target_wallet)

    tracker = WalletTracker(list(wallets))
    try:
        asyncio.run(tracker.start())
    except KeyboardInterrupt:
        logger.info("程序被手动终止")
    except Exception as e:
        logger.error(f"程序异常终止: {e}")
        logger.exception(e)
