from sqlmodel import BIGINT, BLOB, Field

from .base import Base


class RaydiumPoolModel(Base, table=True):
    mint: str = Field(nullable=False, index=True, description="代币 Mint 地址")
    pool_id: str = Field(
        nullable=False, index=True, unique=True, description="流动性池 ID"
    )
    amm_data: bytes = Field(nullable=False, description="AMM 数据", sa_type=BLOB)
    market_data: bytes = Field(nullable=False, description="市场数据", sa_type=BLOB)
    score: int = Field(default=0, description="权重，越高越优先", sa_type=BIGINT)
