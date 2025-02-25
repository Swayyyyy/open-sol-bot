import base64
from typing import Literal

import base58
import httpx
from loguru import logger
from solana.rpc.types import TxOpts
from solders.signature import Signature  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore

from common.config import settings


class JitoClient:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.trading.jito_api,
        )

    async def send_transaction(
        self,
        transaction: VersionedTransaction,
        opts: TxOpts | None = None,
        encoding: Literal["base64", "base58"] = "base64",
    ) -> Signature:
        """Send a signed transaction.

        Args:
            transaction (VersionedTransaction): The signed transaction to send
            opts (TxOpts | None, optional): The transaction options. Defaults to None.

        Returns:
            Signature: The transaction signature
        """
        path = "/api/v1/transactions"
        if opts is None:
            opts = TxOpts(skip_preflight=not settings.trading.preflight_check)

        txn = bytes(transaction)
        if encoding == "base64":
            txn_encoded = base64.b64encode(txn).decode("utf-8")
        elif encoding == "base58":
            txn_encoded = base58.b58encode(txn).decode("utf-8")
        else:
            raise ValueError("encoding must be either 'base64' or 'base58'")

        resp = await self.client.post(
            path,
            json={
                "id": 1,
                "jsonrpc": "2.0",
                "method": "sendTransaction",
                "params": [
                    txn_encoded,
                    {"encoding": encoding},
                ],
            },
        )
        # {
        #     "jsonrpc": "2.0",
        #     "result": "2id3YC2jK9G5Wo2phDx4gJVAew8DcY5NAojnVuao8rkxwPYPe8cSwE5GzhEgJA2y8fVjDEo6iR6ykBvDxrTQrtpb",
        #     "id": 1,
        # }
        js = resp.json()
        bundle_id = resp.headers.get("x-bundle-id")
        sig = Signature.from_string(js["result"])
        logger.info(f"Bundle ID: {bundle_id}, Signature: {sig}")
        return sig
