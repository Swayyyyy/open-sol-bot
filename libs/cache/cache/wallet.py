from solders.pubkey import Pubkey  # type: ignore

from common.config import settings
from common.utils.shyft import ShyftAPI

from .cached import cached


class WalletCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.shyft_api = ShyftAPI(settings.api.shyft_api_key)

    def __repr__(self) -> str:
        return "WalletCache()"

    @cached(ttl=60)  # 1 min
    async def get_sol_balance(self, wallet: str | Pubkey) -> float:
        return await self.shyft_api.get_balance(str(wallet))
