import base64
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey  # type: ignore
from common.layouts.global_account import GlobalAccount
from db.redis import RedisClient
import orjson as json


class GlobalAccountCache:
    def __init__(self, client: AsyncClient) -> None:
        self.celient = client
        self.redis = RedisClient.get_instance()
        self.prefix = "global_account"

    async def _get(self, program: Pubkey) -> bytes | None:
        global_account_pda = Pubkey.find_program_address([b"global"], program)[0]
        token_account = await self.celient.get_account_info_json_parsed(
            global_account_pda
        )
        if token_account is None:
            return None
        value = token_account.value
        if value is None:
            return None
        return bytes(value.data)

    async def get(self, program: Pubkey) -> GlobalAccount | None:
        val = await self.redis.get(f"{self.prefix}:{program}")
        if val is None:
            val = await self._get(program)
            if val is None:
                return None
            data = {"global": base64.b64encode(val).decode()}
            await self.redis.set(f"{self.prefix}:{program}", json.dumps(data))
            return GlobalAccount.from_buffer(val)
        json_data = json.loads(val)
        global_account_bytes = base64.b64decode(json_data["global"])
        return GlobalAccount.from_buffer(global_account_bytes)
