from typing import Dict, List, Optional, Union
from google.protobuf.message import Message
from .solana_storage_pb2 import (
    Transaction,
    TransactionStatusMeta,
    TransactionError,
    Reward,
    UnixTimestamp,
    BlockHeight,
)

class SubscribeRequestFilterAccountsFilterMemcmp(Message):
    offset: int
    data: Union[bytes, str]
    data_type: str

class SubscribeRequestFilterAccountsFilterLamports(Message):
    eq: Optional[int]
    ne: Optional[int]
    lt: Optional[int]
    gt: Optional[int]

class SubscribeRequestFilterAccountsFilter(Message):
    memcmp: Optional[SubscribeRequestFilterAccountsFilterMemcmp]
    datasize: Optional[int]
    token_account_state: Optional[bool]
    lamports: Optional[SubscribeRequestFilterAccountsFilterLamports]

class SubscribeRequestFilterAccounts(Message):
    account: List[str]
    owner: List[str]
    filters: List[SubscribeRequestFilterAccountsFilter]
    nonempty_txn_signature: Optional[bool]

class SubscribeRequestFilterSlots(Message):
    filter_by_commitment: Optional[bool]

class SubscribeRequestFilterTransactions(Message):
    vote: Optional[bool]
    failed: Optional[bool]
    signature: Optional[str]
    account_include: List[str]
    account_exclude: List[str]
    account_required: List[str]

class SubscribeRequestFilterBlocks(Message):
    account_include: List[str]
    include_transactions: Optional[bool]
    include_accounts: Optional[bool]
    include_entries: Optional[bool]

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
    accounts: Dict[str, SubscribeRequestFilterAccounts]
    slots: Dict[str, SubscribeRequestFilterSlots]
    transactions: Dict[str, SubscribeRequestFilterTransactions]
    transactions_status: Dict[str, SubscribeRequestFilterTransactions]
    blocks: Dict[str, SubscribeRequestFilterBlocks]
    blocks_meta: Dict[str, SubscribeRequestFilterBlocksMeta]
    entry: Dict[str, SubscribeRequestFilterEntry]
    commitment: Optional[int]
    accounts_data_slice: List[SubscribeRequestAccountsDataSlice]
    ping: Optional[SubscribeRequestPing]

class SubscribeUpdateAccountInfo(Message):
    pubkey: bytes
    lamports: int
    owner: bytes
    executable: bool
    rent_epoch: int
    data: bytes
    write_version: int
    txn_signature: Optional[bytes]

class SubscribeUpdateAccount(Message):
    account: SubscribeUpdateAccountInfo
    slot: int
    is_startup: bool

class SubscribeUpdateSlot(Message):
    slot: int
    parent: Optional[int]
    status: int
    dead_error: Optional[str]

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
    transactions: List[SubscribeUpdateTransactionInfo]
    updated_account_count: int
    accounts: List[SubscribeUpdateAccountInfo]
    entries_count: int
    entries: List[SubscribeUpdateEntry]

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
    filters: List[str]
    account: Optional[SubscribeUpdateAccount]
    slot: Optional[SubscribeUpdateSlot]
    transaction: Optional[SubscribeUpdateTransaction]
    transaction_status: Optional[SubscribeUpdateTransactionStatus]
    block: Optional[SubscribeUpdateBlock]
    block_meta: Optional[SubscribeUpdateBlockMeta]
    entry: Optional[SubscribeUpdateEntry]
    ping: Optional[SubscribeUpdatePing]
    pong: Optional[SubscribeUpdatePong]

class PingRequest(Message):
    count: int

class PongResponse(Message):
    count: int

class GetLatestBlockhashRequest(Message):
    commitment: Optional[int]

class GetLatestBlockhashResponse(Message):
    slot: int
    blockhash: str
    last_valid_block_height: int

class GetBlockHeightRequest(Message):
    commitment: Optional[int]

class GetBlockHeightResponse(Message):
    block_height: int

class GetSlotRequest(Message):
    commitment: Optional[int]

class GetSlotResponse(Message):
    slot: int

class GetVersionRequest(Message):
    pass

class GetVersionResponse(Message):
    version: str

class IsBlockhashValidRequest(Message):
    blockhash: str
    commitment: Optional[int]

class IsBlockhashValidResponse(Message):
    slot: int
    valid: bool
