from typing import Optional

from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solders.signature import Signature
from solders.transaction import VersionedTransaction

from common.config import settings
from common.log import logger
from common.utils.jito import JitoClient

from .base import TransactionSender


class DefaultTransactionSender(TransactionSender):
    """默认的交易发送器，使用普通 RPC 节点"""

    def __init__(self, client: AsyncClient):
        super().__init__(client)
        self.client: AsyncClient = client

    async def send_transaction(
        self,
        transaction: VersionedTransaction,
        opts: Optional[TxOpts] = None,
    ) -> Signature:
        if opts is None:
            opts = TxOpts(skip_preflight=not settings.trading.preflight_check)

        logger.info("Using default RPC endpoint for transaction")
        resp = await self.client.send_transaction(transaction, opts=opts)
        return resp.value

    async def simulate_transaction(
        self,
        transaction: VersionedTransaction,
    ) -> bool:
        resp = await self.client.simulate_transaction(transaction)
        return resp.value.value.err is None


class JitoTransactionSender(TransactionSender):
    """Jito 交易发送器，使用支持 Jito 的 RPC 节点"""

    def __init__(self, client: JitoClient):
        super().__init__(client)
        self.client: JitoClient = client

    async def send_transaction(
        self,
        transaction: VersionedTransaction,
        opts: Optional[TxOpts] = None,
    ) -> Signature:
        if opts is None:
            opts = TxOpts(skip_preflight=not settings.trading.preflight_check)

        logger.info("Using Jito RPC endpoint for transaction")
        signature = await self.client.send_transaction(transaction, opts=opts)
        return signature

    async def simulate_transaction(
        self,
        transaction: VersionedTransaction,
    ) -> bool:
        raise NotImplementedError("Jito is not implemented yet")
