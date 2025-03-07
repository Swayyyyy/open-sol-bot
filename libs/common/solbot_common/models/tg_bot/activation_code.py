from datetime import datetime

from sqlmodel import BIGINT, Field

from solbot_common.models.base import Base


class ActivationCode(Base, table=True):
    __tablename__ = "bot_activation_codes"  # type: ignore

    code: str = Field(unique=True, nullable=False, min_length=8, max_length=8)
    valid_seconds: int = Field(nullable=False)  # 激活后可用时长（秒）
    used: bool = Field(default=False)  # 是否已使用
    used_by: int | None = Field(default=None, nullable=True, sa_type=BIGINT)  # 使用者的 chat_id
    used_at: datetime | None = Field(default=None, nullable=True)  # 使用时间
