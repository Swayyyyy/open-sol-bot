from abc import ABC, abstractmethod
from typing import Optional

from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solders.signature import Signature
from solders.transaction import VersionedTransaction

from common.utils.jito import JitoClient


class TransactionSender(ABC):
    """交易发送器的抽象基类"""

    def __init__(self, client: AsyncClient | JitoClient):
        self.client = client

    @abstractmethod
    async def send_transaction(
        self,
        transaction: VersionedTransaction,
        opts: Optional[TxOpts] = None,
    ) -> Signature:
        """发送交易

        Args:
            transaction (VersionedTransaction): 要发送的交易
            opts (Optional[TxOpts], optional): 交易选项. Defaults to None.

        Returns:
            Signature: 交易签名
        """
        pass

    @abstractmethod
    async def simulate_transaction(
        self,
        transaction: VersionedTransaction,
    ) -> bool:
        """模拟交易

        Args:
            transaction (VersionedTransaction): 要模拟的交易

        Returns:
            bool: 模拟是否成功
        """
        pass
