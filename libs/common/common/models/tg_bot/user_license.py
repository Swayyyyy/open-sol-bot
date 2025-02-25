from sqlmodel import BIGINT, Field

from common.models.base import Base


class UserLicense(Base, table=True):
    __tablename__ = "bot_user_licenses"  # type: ignore

    chat_id: int = Field(unique=True, nullable=False, sa_type=BIGINT)
    expired_timestamp: int = Field(default=0)  # 剩余可用时长（分钟）
