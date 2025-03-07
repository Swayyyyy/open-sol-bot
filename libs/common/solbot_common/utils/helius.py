import httpx

from solbot_common.config import settings


class HeliusAPI:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.api.helius_api_base_url,
            params={
                "api-key": settings.api.helius_api_key,
                "commitment": "confirmed",
            },
        )

    async def get_parsed_transaction(self, tx_hash: str) -> dict:
        """获取交易详情"""
        response = await self.client.post(
            "/transactions",
            json={
                "transactions": [tx_hash],
            },
        )
        response.raise_for_status()
        return response.json()
