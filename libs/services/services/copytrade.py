from typing import List, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from common.models.tg_bot.copytrade import CopyTrade
from db.session import NEW_ASYNC_SESSION, provide_session


class CopyTradeService:
    @classmethod
    @provide_session
    async def get_by_target_wallet(
        cls, target_wallet: str, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> List[CopyTrade]:
        """ "获取指定目标钱包的活跃跟单"""
        stmt = select(CopyTrade).where(
            CopyTrade.target_wallet == target_wallet and CopyTrade.active == True
        )
        results = await session.execute(stmt)
        return [row.model_copy() for row in results.scalars().all()]

    @classmethod
    @provide_session
    async def get_active_wallet_addresses(
        cls, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> Sequence[str]:
        """获取所有已激活的目标钱包地址

        Returns:
            Sequence[str]: 已激活的目标钱包地址列表，去重后的结果
        """
        stmt = (
            select(CopyTrade.target_wallet).where(CopyTrade.active == True).distinct()
        )
        result = await session.execute(stmt)
        return result.scalars().all()
