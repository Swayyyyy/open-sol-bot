from sqlalchemy import BIGINT
from sqlmodel import Field

from solbot_common.models.base import Base


class Holding(Base, table=True):
    __tablename__ = "bot_holdings"  # type: ignore
    wallet_address: str = Field(nullable=True, index=True, description="钱包地址")
    mint: str = Field(nullable=False, description="代币地址")
    associated_account: str = Field(nullable=False, description="关联账户")
    symbol: str = Field(nullable=False, description="代币符号")
    decimals: int = Field(nullable=False, description="代币精度")
    amount: int = Field(nullable=False, sa_type=BIGINT, description="余额")
