from dataclasses import dataclass

from solders.pubkey import Pubkey  # type: ignore
from typing_extensions import Self

from .layouts import MINT_LAYOUT


@dataclass
class MintAccount:
    mint_authority_option: int
    mint_authority: str
    supply: int
    decimals: int
    is_initialized: bool
    freeze_authority_option: int
    freeze_authority: str

    @classmethod
    def from_buffer(cls, buffer: bytes) -> Self:
        """
        从字节缓冲区解析账户数据
        """
        decoded_data = MINT_LAYOUT.parse(buffer)
        mint_authority_option = decoded_data.mint_authority_option
        mint_authority = Pubkey.from_bytes(decoded_data.mint_authority)
        supply = decoded_data.supply
        decimals = decoded_data.decimals
        is_initialized = decoded_data.is_initialized
        freeze_authority_option = decoded_data.freeze_authority_option
        freeze_authority = Pubkey.from_bytes(decoded_data.freeze_authority)

        return cls(
            mint_authority_option=mint_authority_option,
            mint_authority=mint_authority.__str__(),
            supply=supply,
            decimals=decimals,
            is_initialized=is_initialized,
            freeze_authority_option=freeze_authority_option,
            freeze_authority=freeze_authority.__str__(),
        )
