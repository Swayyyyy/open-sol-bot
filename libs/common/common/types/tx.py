from dataclasses import asdict, dataclass
from enum import Enum
from typing import Literal, TypedDict

import orjson as json


class TxType(Enum):
    OPEN_POSITION = "open_position"  # 开仓
    ADD_POSITION = "add_position"  # 加仓
    REDUCE_POSITION = "reduce_position"  # 减仓
    CLOSE_POSITION = "close_position"  # 清仓
    ERROR_ORDER = 'error_order'  # 错误订单


@dataclass
class TxEvent:
    signature: str
    from_amount: int
    from_decimals: int
    to_amount: int
    to_decimals: int
    mint: str  # token mint
    who: str  # smart wallet
    tx_type: TxType
    tx_direction: Literal["buy", "sell"]
    timestamp: int
    pre_token_amount: int
    post_token_amount: int
    program_id: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self)).decode("utf-8")

    @classmethod
    def from_json(cls, tx_detail: str) -> "TxEvent":
        obj = cls(**json.loads(tx_detail))
        obj.tx_type = TxType(obj.tx_type)
        return obj


class TokenAmountChange(TypedDict):
    change_amount: int
    decimals: int
    pre_balance: int
    post_balance: int


class SolAmountChange(TypedDict):
    change_amount: int
    decimals: int
    pre_balance: int
    post_balance: int
