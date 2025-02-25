from sqlalchemy import BIGINT, BLOB
from sqlmodel import Field, Index, UniqueConstraint

from common.models.base import Base


class User(Base, table=True):
    __tablename__ = "bot_users"  # type: ignore
    chat_id: int = Field(nullable=False, index=True, sa_type=BIGINT)
    pubkey: str = Field(
        nullable=False, index=True, unique=True, description="User public key"
    )
    private_key: bytes | None = Field(
        nullable=True, sa_type=BLOB, description="User private key"
    )
    is_default: bool = Field(
        nullable=False, default=False, description="是否为用户的默认钱包"
    )
    is_active: bool = Field(nullable=False, default=True, description="是否启用")

    # 一个 chat id 只能有一个默认钱包
    # 联合 chat_id 和 is_default 索引
    # 添加联合唯一约束和索引
    __table_args__ = (
        UniqueConstraint("chat_id", "is_default", name="uq_chat_default_wallet"),
        Index("ix_chat_default", "chat_id", "is_default"),
    )
