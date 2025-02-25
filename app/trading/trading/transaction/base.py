from abc import ABC, abstractmethod

from solana.rpc.async_api import AsyncClient
from solders.signature import Signature  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore


class TransactionSender(ABC):
    """交易发送器的抽象基类"""

    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client

    @abstractmethod
    async def send_transaction(
        self,
        transaction: VersionedTransaction,
        **kwargs,
    ) -> Signature:
        """发送交易

        Args:
            transaction (VersionedTransaction): 要发送的交易
            **kwargs: 可选的关键字参数

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
