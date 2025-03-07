from enum import Enum

from sqlalchemy import BIGINT
from sqlmodel import Field

from solbot_common.layouts.token_account import TokenAccount
from solbot_common.models.base import Base
from solbot_common.utils.utils import get_associated_token_address


class State(Enum):
    UNINITIALIZED = "uninitialized"  # 未初始化或已关闭
    INITIALIZED = "initialized"  # 正常状态
    FROZEN = "frozen"  # 被冻结
    CLOSED = "closed"  # 已关闭


class AssociatedTokenAccount(Base, table=True):
    __tablename__ = "associated_token_accounts"  # type: ignore

    owner: str = Field(nullable=False)
    mint: str = Field(nullable=False, index=True)
    associated_token_account: str = Field(nullable=False, index=True)
    amount: int = Field(nullable=False, sa_type=BIGINT)
    decimals: int = Field(nullable=False)
    state: State = Field(default=State.UNINITIALIZED)

    # 联合唯一索引
    __unique_together__ = ("owner", "mint")

    @classmethod
    def from_token_account(cls, token_account: TokenAccount, decimals: int):
        if token_account.state == 0:
            state = State.UNINITIALIZED
        elif token_account.state == 1:
            state = State.INITIALIZED
        elif token_account.state == 2:
            state = State.FROZEN
        elif token_account.state == 3:
            state = State.CLOSED
        else:
            state = State.UNINITIALIZED

        associated_token_account = get_associated_token_address(
            token_account.owner, token_account.mint
        )
        if associated_token_account is None:
            return

        return cls(
            owner=token_account.owner.__str__(),
            mint=token_account.mint.__str__(),
            amount=token_account.amount,
            decimals=decimals,
            associated_token_account=associated_token_account.__str__(),
            state=state,
        )
