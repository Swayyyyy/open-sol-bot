from dataclasses import dataclass


@dataclass
class Monitor:
    chat_id: int
    pk: int | None = None  # primary key
    target_wallet: str | None = None
    wallet_alias: str | None = None
    active: bool = True
