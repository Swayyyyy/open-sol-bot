from typing import TypedDict

import httpx


class TransactionStatus(TypedDict):
    success: bool
    failed: bool
    expired: bool


class GmgnAPI:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="https://gmgn.ai",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

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
