from sqlmodel import Field

from solbot_common.layouts.mint_account import MintAccount as LayoutMintAccount
from solbot_common.models.base import Base


class MintAccount(Base, table=True):
    __tablename__ = "mint_accounts"  # type: ignore

    mint: str = Field(nullable=False, index=True, unique=True)
    bin: bytes = Field(nullable=False)

    def to_mint_account(self) -> LayoutMintAccount:
        return LayoutMintAccount.from_buffer(self.bin)
