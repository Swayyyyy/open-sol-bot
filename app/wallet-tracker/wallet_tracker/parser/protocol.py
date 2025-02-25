from functools import cache
from typing import Protocol

from common.types import SolAmountChange, TokenAmountChange, TxEvent, TxType


class TransactionParserInterface(Protocol):
    tx_detail: dict

    @cache
    def get_block_time(self) -> int: ...

    @cache
    def get_tx_hash(self) -> str: ...

    @cache
    def get_who(self) -> str: ...

    @cache
    def get_mint(self) -> str: ...

    @cache
    def get_token_amount_change(self) -> TokenAmountChange: ...

    @cache
    def get_sol_amount_change(self) -> SolAmountChange: ...

    @cache
    def get_tx_type(self) -> TxType: ...

    def parse(self) -> TxEvent: ...
