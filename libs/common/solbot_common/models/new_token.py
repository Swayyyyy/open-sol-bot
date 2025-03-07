from pydantic import ConfigDict
from sqlmodel import Field

from solbot_common.models.base import Base

# {
#     "signature": "4uTy6e7h2SyxuwMyGsJ2Mxh3Rrj99CFeQ6uF1H8xFsEzW8xfrUZ9Xb8QxYutd5zt2cutP45CSPX3CypMAc3ykr2q",
#     "mint": "DjmgD4sawByggagUqjxXqs9hAxAXb7Nf76Pzrk9npump",
#     "traderPublicKey": "Brw8BKYSkpYtYCmHdhxd61itAw6K4qbcUMJWqm3Ak54z",
#     "txType": "create",
#     "initialBuy": 47840764.33121,
#     "bondingCurveKey": "5S7xw3VbXFC7H4Aj4vxkxzq6hUzg7M3bi11AWrGg8d2Q",
#     "vTokensInBondingCurve": 1025159235.66879,
#     "vSolInBondingCurve": 31.399999999999995,
#     "marketCapSol": 30.629388008698342,
#     "name": "Doggy",
#     "symbol": "Doggy",
#     "uri": "https://ipfs.io/ipfs/QmWwozKDWaoqVjygauFrRZSyz4o73gVtQ5kRazKqKHTuDk"
# }


class NewToken(Base, table=True):
    __tablename__ = "new_tokens"  # type: ignore

    model_config = ConfigDict(populate_by_name=True)  # type: ignore

    signature: str = Field(nullable=False, alias="signature")
    mint: str = Field(nullable=False, unique=True, index=True, alias="mint")
    name: str = Field(nullable=False, alias="name")
    symbol: str = Field(nullable=False, alias="symbol")
    uri: str = Field(nullable=False, alias="uri")

    trader_public_key: str | None = Field(
        nullable=True,
        alias="traderPublicKey",
    )
    tx_type: str | None = Field(
        nullable=True,
        alias="txType",
    )
    initial_buy: float | None = Field(
        nullable=True,
        alias="initialBuy",
    )
    bonding_curve_key: str | None = Field(
        nullable=True,
        alias="bondingCurveKey",
    )
    v_tokens_in_bonding_curve: float | None = Field(
        nullable=True,
        alias="vTokensInBondingCurve",
    )
    v_sol_in_bonding_curve: float | None = Field(
        nullable=True,
        alias="vSolInBondingCurve",
    )
    market_cap_sol: float | None = Field(
        nullable=True,
        alias="marketCapSol",
    )
