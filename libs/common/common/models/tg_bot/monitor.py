from typing import Sequence
from sqlmodel import Field, select
from sqlalchemy import BIGINT
from common.models.base import Base


class Monitor(Base, table=True):
    __tablename__ = "bot_monitor"  # type: ignore
    chat_id: int = Field(
        nullable=False, index=True, sa_type=BIGINT, description="用户 ID"
    )
    target_wallet: str = Field(nullable=False)
    wallet_alias: str | None = Field(nullable=True)
    active: bool = Field(nullable=False, description="是否激活")

    @classmethod
    async def get_active_wallet_addresses(cls) -> Sequence[str]:
        """获取所有已激活的目标钱包地址

        Returns:
            Sequence[str]: 已激活的目标钱包地址列表，去重后的结果
        """
        from db.session import start_async_session

        async with start_async_session() as session:
            # 查询所有激活的监听器，只选择 target_wallet 字段
            stmt = (
                select(cls.target_wallet)
                .where(cls.active == True)  # noqa: E712
                .distinct()
            )
            result = await session.execute(stmt)
            return result.scalars().all()
