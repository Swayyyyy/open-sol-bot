from asyncio import Queue

from solbot_common.layouts.mint_account import MintAccount
from solbot_common.log import logger
from solbot_common.models import MintAccount as ModelMintAccount
from solbot_common.utils import get_async_client
from solbot_db.session import NEW_ASYNC_SESSION, provide_session, start_async_session
from solders.pubkey import Pubkey  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing_extensions import Self


class MintAccountBackgoundWriter:
    def __init__(self):
        super().__init__()
        self.queue = Queue()

    async def submit(self, mint: Pubkey, bin_: bytes):
        await self.queue.put((mint, bin_))

    async def run(self):
        while True:
            result = await self.queue.get()
            if result is None:
                break
            mint, bin_ = result
            async with start_async_session() as session:
                session.add(ModelMintAccount(mint=str(mint), bin=bin_))
                try:
                    await session.commit()
                except Exception as e:
                    logger.error(f"Failed to store mint account: {mint}")
                    logger.error(e)

                logger.info(f"Stored mint account: {mint}")
            self.queue.task_done()

    def stop(self):
        self.queue.put_nowait(None)


class MintAccountCache:
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.client = get_async_client()
        self._writer = MintAccountBackgoundWriter()

    @provide_session
    async def get_mint_account(
        self, mint: Pubkey | str, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> MintAccount | None:
        if isinstance(mint, str):
            mint = Pubkey.from_string(mint)
        if not isinstance(mint, Pubkey):
            raise ValueError("Mint must be a string")

        mint_account = None
        smtm = select(ModelMintAccount).where(ModelMintAccount.mint == mint.__str__())
        record = (await session.execute(statement=smtm)).scalar_one_or_none()
        if record is not None:
            mint_account = record.to_mint_account()

        if mint_account is not None:
            return mint_account

        logger.warning(f"Did not find mint account in cache: {mint}, fetching...")

        response = await self.client.get_account_info(mint)
        account = response.value
        if account is None:
            return None
        mint_account = MintAccount.from_buffer(account.data)

        await self._writer.submit(mint, account.data)
        return mint_account

    def __del__(self):
        self._writer.stop()
