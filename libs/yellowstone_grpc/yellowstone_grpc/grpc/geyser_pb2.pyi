from google.protobuf.message import Message

from .solana_storage_pb2 import (
    BlockHeight,
    Reward,
    Transaction,
    TransactionError,
    TransactionStatusMeta,
    UnixTimestamp,
)

class SubscribeRequestFilterAccountsFilterMemcmp(Message):
    offset: int
    data: bytes | str
    data_type: str

class SubscribeRequestFilterAccountsFilterLamports(Message):
    eq: int | None
    ne: int | None
    lt: int | None
    gt: int | None

class SubscribeRequestFilterAccountsFilter(Message):
    memcmp: SubscribeRequestFilterAccountsFilterMemcmp | None
    datasize: int | None
    token_account_state: bool | None
    lamports: SubscribeRequestFilterAccountsFilterLamports | None

class SubscribeRequestFilterAccounts(Message):
    account: list[str]
    owner: list[str]
    filters: list[SubscribeRequestFilterAccountsFilter]
    nonempty_txn_signature: bool | None

class SubscribeRequestFilterSlots(Message):
    filter_by_commitment: bool | None

class SubscribeRequestFilterTransactions(Message):
    vote: bool | None
    failed: bool | None
    signature: str | None
    account_include: list[str]
    account_exclude: list[str]
    account_required: list[str]

class SubscribeRequestFilterBlocks(Message):
    account_include: list[str]
    include_transactions: bool | None
    include_accounts: bool | None
    include_entries: bool | None

class SubscribeRequestFilterBlocksMeta(Message):
    pass

class SubscribeRequestFilterEntry(Message):
    pass

class SubscribeRequestAccountsDataSlice(Message):
    offset: int
    length: int

class SubscribeRequestPing(Message):
    id: int

class SubscribeRequest(Message):
    accounts: dict[str, SubscribeRequestFilterAccounts]
    slots: dict[str, SubscribeRequestFilterSlots]
    transactions: dict[str, SubscribeRequestFilterTransactions]
    transactions_status: dict[str, SubscribeRequestFilterTransactions]
    blocks: dict[str, SubscribeRequestFilterBlocks]
    blocks_meta: dict[str, SubscribeRequestFilterBlocksMeta]
    entry: dict[str, SubscribeRequestFilterEntry]
    commitment: int | None
    accounts_data_slice: list[SubscribeRequestAccountsDataSlice]
    ping: SubscribeRequestPing | None

class SubscribeUpdateAccountInfo(Message):
    pubkey: bytes
    lamports: int
    owner: bytes
    executable: bool
    rent_epoch: int
    data: bytes
    write_version: int
    txn_signature: bytes | None

class SubscribeUpdateAccount(Message):
    account: SubscribeUpdateAccountInfo
    slot: int
    is_startup: bool

class SubscribeUpdateSlot(Message):
    slot: int
    parent: int | None
    status: int
    dead_error: str | None

class SubscribeUpdateTransactionInfo(Message):
    signature: bytes
    is_vote: bool
    transaction: Transaction
    meta: TransactionStatusMeta
    index: int

class SubscribeUpdateTransaction(Message):
    transaction: SubscribeUpdateTransactionInfo
    slot: int

class SubscribeUpdateTransactionStatus(Message):
    slot: int
    signature: bytes
    is_vote: bool
    index: int
    err: TransactionError

class SubscribeUpdateEntry(Message):
    slot: int
    index: int
    num_hashes: int
    hash: bytes
    executed_transaction_count: int
    starting_transaction_index: int

class SubscribeUpdateBlock(Message):
    slot: int
    blockhash: str
    rewards: list[Reward]
    block_time: UnixTimestamp
    block_height: BlockHeight
    parent_slot: int
    parent_blockhash: str
    executed_transaction_count: int
    transactions: list[SubscribeUpdateTransactionInfo]
    updated_account_count: int
    accounts: list[SubscribeUpdateAccountInfo]
    entries_count: int
    entries: list[SubscribeUpdateEntry]

class SubscribeUpdateBlockMeta(Message):
    slot: int
    blockhash: str
    rewards: list[Reward]
    block_time: UnixTimestamp
    block_height: BlockHeight
    parent_slot: int
    parent_blockhash: str
    executed_transaction_count: int
    entries_count: int

class SubscribeUpdatePing(Message):
    pass

class SubscribeUpdatePong(Message):
    id: int

class SubscribeUpdate(Message):
    filters: list[str]
    account: SubscribeUpdateAccount | None
    slot: SubscribeUpdateSlot | None
    transaction: SubscribeUpdateTransaction | None
    transaction_status: SubscribeUpdateTransactionStatus | None
    block: SubscribeUpdateBlock | None
    block_meta: SubscribeUpdateBlockMeta | None
    entry: SubscribeUpdateEntry | None
    ping: SubscribeUpdatePing | None
    pong: SubscribeUpdatePong | None

class PingRequest(Message):
    count: int

class PongResponse(Message):
    count: int

class GetLatestBlockhashRequest(Message):
    commitment: int | None

class GetLatestBlockhashResponse(Message):
    slot: int
    blockhash: str
    last_valid_block_height: int

class GetBlockHeightRequest(Message):
    commitment: int | None

class GetBlockHeightResponse(Message):
    block_height: int

class GetSlotRequest(Message):
    commitment: int | None

class GetSlotResponse(Message):
    slot: int

class GetVersionRequest(Message):
    pass

class GetVersionResponse(Message):
    version: str

class IsBlockhashValidRequest(Message):
    blockhash: str
    commitment: int | None

class IsBlockhashValidResponse(Message):
    slot: int
    valid: bool
