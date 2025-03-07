import asyncio
from typing import TypedDict

from solbot_common.config import settings
from solbot_common.log import logger
from solbot_common.models import TokenInfo
from solbot_common.utils import get_async_client
from solbot_common.utils.shyft import ShyftAPI
from solbot_db.session import NEW_ASYNC_SESSION, provide_session, start_async_session
from solders.pubkey import Pubkey  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing_extensions import Self

from solbot_cache.cached import cached


# {
#   "status": "Success",
#   "message": "Retrieved Token Info from Token Hash",
#   "result": {
#     "tokenHash": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
#     "data": {
#       "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
#       "tokenName": "USD Coin",
#       "symbol": "USDC",
#       "decimals": 6,
#       "description": "",
#       "logo": "https://s3.coinmarketcap.com/static-gravity/image/5a8229787b5e4c809b5914eef709b59a.png",
#       "tags": [
#         "stablecoin",
#         "saber-mkt-usd"
#       ],
#       "verified": "true",
#       "network": [
#         "mainnet"
#       ],
#       "metadataToken": ""
#     }
#   }
# }
class TokenInfoDict(TypedDict):
    mint: str
    tokenName: str
    symbol: str
    decimals: int
    description: str
    logo: str
    tags: list[str]
    verified: str
    network: list[str]
    metadataToken: str


class TokenInfoCache:
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.rpc_client = get_async_client()
        self.shyft_api = ShyftAPI(settings.api.shyft_api_key)

    def __repr__(self) -> str:
        return "TokenInfoCache()"

    @cached(ttl=60 * 60 * 24)
    @provide_session
    async def get(
        self, mint: Pubkey | str, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> TokenInfo | None:
        if isinstance(mint, str):
            try:
                mint = Pubkey.from_string(mint)
            except ValueError:
                raise ValueError(f"Invalid Base58 string: {mint}")

        if not isinstance(mint, Pubkey):
            raise ValueError("Mint must be a string")

        smtm = select(TokenInfo).where(TokenInfo.mint == mint.__str__())
        token_info = (await session.execute(statement=smtm)).scalar_one_or_none()
        if token_info is not None:
            # 返回一个副本以避免 session 相关的问题
            return token_info.model_copy()

        logger.info(f"Did not find token info in cache: {mint}, fetching...")

        try:
            data = await self.shyft_api.get_token_info(mint.__str__())
            token_info = TokenInfo(
                mint=data["address"],
                token_name=data["name"],
                symbol=data["symbol"],
                decimals=data["decimals"],
            )

            async def _write_to_db():
                _token_info = token_info.model_copy()
                async with start_async_session() as session:
                    existing = await session.execute(
                        select(TokenInfo).where(TokenInfo.mint == _token_info.mint)
                    )
                    existing_token = existing.scalar_one_or_none()

                    if existing_token:
                        existing_token.token_name = _token_info.token_name
                        existing_token.symbol = _token_info.symbol
                        existing_token.decimals = _token_info.decimals
                    else:
                        session.add(_token_info)

                    try:
                        await session.commit()
                        logger.info(
                            f"{'Updated' if existing_token else 'Stored'} token info: {mint}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to {'update' if existing_token else 'store'} token info: {mint}, cause: {e}"
                        )
                        await session.rollback()

            db_task = asyncio.create_task(_write_to_db())
            # 添加任务完成回调以处理可能的异常
            db_task.add_done_callback(lambda t: t.exception() if t.exception() else None)
        except Exception as e:
            logger.warning(f"Failed to fetch token info: {mint}, cause: {e}")
            return None

        return token_info.model_copy()
