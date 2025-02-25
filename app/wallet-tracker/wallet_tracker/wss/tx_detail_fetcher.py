from common.config import settings
import orjson as json
from solders.signature import Signature  # type: ignore
from solana.rpc.async_api import AsyncClient
import httpx
from common.log import logger


class TxDetailRawFetcher:
    def __init__(self, rpc_url: str = settings.rpc.rpc_url) -> None:
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)

    async def fetch(self, signature: Signature) -> dict | None:
        logger.debug(f"Fetching transaction from {self.rpc_url}")
        resp = await self.client.get_transaction(
            signature,
            encoding="json",
            commitment=settings.rpc.commitment,
            max_supported_transaction_version=0,
        )
        data = json.loads(resp.to_json())
        if "result" not in data:
            raise Exception(f"Error message: {data}")
        return data["result"]


class TxDetailShyftFetcher:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.api.shyft_api_base_url,
            headers={"X-Api-Key": settings.api.shyft_api_key},
        )

    async def fetch(self, signature: Signature) -> dict | None:
        path = f"/sol/v1/transaction/raw?network=mainnet-beta&txn_signature={signature}"
        response = await self.client.get(path, timeout=3)
        response.raise_for_status()
        resp_json = response.json()

        if resp_json.get("success") is True:
            return resp_json["result"]
        else:
            raise Exception(f"Error message: {resp_json['message']}")


async def fetch_tx_detail_from_solscan(
    signature: Signature, session: httpx.AsyncClient | None = None
) -> dict | None:
    if session is None:
        session = httpx.AsyncClient()

    async with session as client:
        api_base_url = settings.api.solscan_api_base_url
        url = f"{api_base_url}/transaction/detail?tx={signature}"
        response = await client.get(url)
        response.raise_for_status()
        resp_json = response.json()

    if resp_json.get("success") is True:
        return resp_json["data"]
    else:
        error_code = resp_json["errors"]["code"]
        error_msg = resp_json["errors"]["message"]
        raise Exception(f"Error code: {error_code}, Error message: {error_msg}")
