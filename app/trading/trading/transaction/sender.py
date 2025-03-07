import base64

from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solbot_common.config import settings
from solbot_common.log import logger
from solbot_common.utils.gmgn import GmgnAPI
from solbot_common.utils.jito import JitoClient
from solders.signature import Signature  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore

from .base import TransactionSender


class DefaultTransactionSender(TransactionSender):
    """默认的交易发送器，使用普通 RPC 节点"""

    def __init__(self, client: AsyncClient):
        super().__init__(client)
        self.client: AsyncClient = client

    async def send_transaction(
        self,
        transaction: VersionedTransaction,
        opts: TxOpts | None = None,
        **kwargs,
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

    def __init__(self, rpc_client: AsyncClient):
        super().__init__(rpc_client)
        self.jito_client: JitoClient = JitoClient()

    async def send_transaction(
        self,
        transaction: VersionedTransaction,
        opts: TxOpts | None = None,
        **kwargs,
    ) -> Signature:
        if opts is None:
            opts = TxOpts(skip_preflight=not settings.trading.preflight_check)

        logger.info("Using Jito RPC endpoint for transaction")
        signature = await self.jito_client.send_transaction(transaction, opts=opts)
        return signature

    async def simulate_transaction(
        self,
        transaction: VersionedTransaction,
    ) -> bool:
        raise NotImplementedError("Jito is not implemented yet")


class GMGNTransactionSender(TransactionSender):
    """GMGN 交易发送器"""

    def __init__(self, rpc_client: AsyncClient) -> None:
        self.rpc_client: AsyncClient = rpc_client
        self.gmgn_client = GmgnAPI()

    async def send_transaction(
        self,
        transaction: VersionedTransaction,
        **kwargs,
    ) -> Signature:
        logger.info("Using GMGN RPC endpoint for transaction")
        encoded_tx = base64.b64encode(bytes(transaction)).decode("utf-8")
        return await self.gmgn_client.submit_signed_transaction(signed_tx=encoded_tx)

    async def simulate_transaction(
        self,
        transaction: VersionedTransaction,
    ) -> bool:
        resp = await self.rpc_client.simulate_transaction(transaction)
        return resp.value.value.err is None
