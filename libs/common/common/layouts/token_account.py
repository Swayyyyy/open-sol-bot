from .layouts import TOKEN_ACCOUNT_LAYOUT
from solders.pubkey import Pubkey
from dataclasses import dataclass
from typing_extensions import Self


@dataclass
class TokenAccount:
    mint: Pubkey
    owner: Pubkey
    amount: int
    delegate: Pubkey | None
    state: int
    is_native_option: int
    is_native: int
    delegated_amount: int
    close_authority_option: int
    close_authority: Pubkey | None

    @classmethod
    def from_buffer(cls, buffer: bytes) -> Self | None:
        decoded_data = TOKEN_ACCOUNT_LAYOUT.parse(buffer)
        mint = Pubkey.from_bytes(decoded_data.mint)
        owner = Pubkey.from_bytes(decoded_data.owner)
        amount = decoded_data.amount
        delegate = decoded_data.delegate_option == 1
        delegate_address = (
            Pubkey.from_bytes(decoded_data.delegate) if delegate else None
        )
        state = decoded_data.state
        is_native = decoded_data.is_native_option == 1
        delegated_amount = decoded_data.delegated_amount if delegate else 0
        close_authority = decoded_data.close_authority_option == 1
        close_authority_address = (
            Pubkey.from_bytes(decoded_data.close_authority) if close_authority else None
        )

        try:
            return cls(
                mint=mint,
                owner=owner,
                amount=amount,
                delegate=delegate_address,
                state=state,
                is_native_option=decoded_data.is_native_option,
                is_native=is_native,
                delegated_amount=delegated_amount,
                close_authority_option=decoded_data.close_authority_option,
                close_authority=close_authority_address,
            )
        except Exception:
            return None
