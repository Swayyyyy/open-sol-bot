from solbot_common.utils.utils import get_async_client
from solders.pubkey import Pubkey  # type: ignore


class AccountAmountCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._client = get_async_client()

    async def get_amount(self, pubkey: Pubkey) -> int:
        in_account = await self._client.get_account_info_json_parsed(pubkey)
        if in_account.value is None:
            raise Exception("in_account not found")
        # TODO: 目前没有实现缓存
        #  缓存思路，需要监听自己钱包的所有 token 的余额变化
        amount = in_account.value.data.parsed["info"]["tokenAmount"]["amount"]  # type: ignore
        return int(amount)  # type: ignore
