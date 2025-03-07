from typing import TypedDict

import httpx
from solders.signature import Signature  # type: ignore


class TransactionStatus(TypedDict):
    success: bool
    failed: bool
    expired: bool


class BundleTransactionResult(TypedDict):
    order_id: str
    bundle_id: str
    last_valid_block_number: int
    tx_hash: str


class GmgnAPI:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="https://gmgn.ai",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    async def submit_signed_transaction(self, signed_tx: str) -> Signature:
        """提交交易
        Args:
            signed_tx (str): 交易签名, base64 编码
        Returns:
            Signature: 交易签名
        """
        url = "/defi/router/v1/sol/tx/submit_signed_transaction"
        data = {"signed_tx": signed_tx}

        response = await self.client.post(url, json=data)
        response.raise_for_status()
        js = response.json()
        if js["code"] != 0:
            raise ValueError(js["msg"])
        return Signature.from_string(js["data"]["hash"])

    async def submit_bundle_transaction(
        self, signed_tx: str, from_address: str
    ) -> BundleTransactionResult:
        """提交交易

        Args:
            signed_tx (str): 交易签名, base64 编码
            from_address (str): 交易发起者地址
        Returns:
            BundleTransactionResult: 交易信息
        """
        url = "/defi/router/v1/sol/tx/submit_signed_bundle_transaction"
        data = {"signed_tx": signed_tx, "from_address": from_address}

        response = await self.client.post(url, json=data)
        response.raise_for_status()
        js = response.json()
        if js["code"] != 0:
            raise ValueError(js["msg"])
        return js["data"]

    async def get_swap_transaction(
        self,
        token_in_address: str,
        token_out_address: str,
        in_amount: str,
        from_address: str,
        slippage: int,
        swap_mode: str,
        fee: float,
    ) -> str:
        params = {
            "token_in_address": token_in_address,
            "token_out_address": token_out_address,
            "in_amount": in_amount,
            "from_address": from_address,
            "slippage": slippage,
            "swap_mode": swap_mode,
            "fee": fee,
        }
        response = await self.client.get(
            "/defi/router/v1/sol/tx/get_swap_route",
            params=params,
        )
        response.raise_for_status()
        js = response.json()
        if js["code"] != 0:
            raise ValueError("Error: {}, Argument: {}".format(js["msg"], params))

        data = js["data"]
        raw_tx = data["raw_tx"]
        swap_tx = raw_tx["swapTransaction"]
        return swap_tx

    async def get_transaction_status(
        self, tx_hash: str, last_valid_height: int
    ) -> TransactionStatus:
        """获取交易状态

        Args:
            tx_hash (str): 交易hash
            last_valid_height (int): 最后有效高度
        Returns:
            dict: 交易状态
        """
        params = {
            "hash": tx_hash,
            "last_valid_height": last_valid_height,
        }
        response = await self.client.get(
            "/defi/router/v1/sol/tx/get_transaction_status",
            params=params,
        )
        response.raise_for_status()
        js = response.json()
        if js["code"] != 0:
            raise Exception("Error: {}, Argument: {}".format(js["msg"], params))
        return js["data"]
