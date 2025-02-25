from typing import List, Optional
from google.protobuf.message import Message as _Message

class MessageHeader(_Message):
    num_required_signatures: int
    num_readonly_signed_accounts: int
    num_readonly_unsigned_accounts: int

class MessageAddressTableLookup(_Message):
    account_key: bytes
    writable_indexes: bytes
    readonly_indexes: bytes

class CompiledInstruction(_Message):
    program_id_index: int
    accounts: bytes
    data: bytes

class Message(_Message):
    header: MessageHeader
    account_keys: List[bytes]
    recent_blockhash: bytes
    instructions: List[CompiledInstruction]
    versioned: bool
    address_table_lookups: List[MessageAddressTableLookup]

class Transaction(_Message):
    signatures: List[bytes]
    message: Message

class UiTokenAmount(_Message):
    ui_amount: float
    decimals: int
    amount: str
    ui_amount_string: str

class TokenBalance(_Message):
    account_index: int
    mint: str
    ui_token_amount: UiTokenAmount
    owner: str
    program_id: str

class ReturnData(_Message):
    program_id: bytes
    data: bytes

class InnerInstruction(_Message):
    program_id_index: int
    accounts: bytes
    data: bytes
    stack_height: Optional[int]

class InnerInstructions(_Message):
    index: int
    instructions: List[InnerInstruction]

class TransactionError(_Message):
    err: bytes

class TransactionStatusMeta(_Message):
    err: Optional[TransactionError]
    fee: int
    pre_balances: List[int]
    post_balances: List[int]
    inner_instructions: List[InnerInstructions]
    inner_instructions_none: bool
    log_messages: List[str]
    log_messages_none: bool
    pre_token_balances: List[TokenBalance]
    post_token_balances: List[TokenBalance]
    rewards: List["Reward"]
    loaded_writable_addresses: List[bytes]
    loaded_readonly_addresses: List[bytes]
    return_data: Optional[ReturnData]
    return_data_none: bool
    compute_units_consumed: Optional[int]

class ConfirmedTransaction(_Message):
    transaction: Transaction
    meta: TransactionStatusMeta

class Reward(_Message):
    pubkey: str
    lamports: int
    post_balance: int
    reward_type: int
    commission: str

class Rewards(_Message):
    rewards: List[Reward]
    num_partitions: NumPartitions

class UnixTimestamp(_Message):
    timestamp: int

class BlockHeight(_Message):
    block_height: int

class NumPartitions(_Message):
    num_partitions: int

class ConfirmedBlock(_Message):
    previous_blockhash: str
    blockhash: str
    parent_slot: int
    transactions: List[ConfirmedTransaction]
    rewards: List[Reward]
    block_time: UnixTimestamp
    block_height: BlockHeight
    num_partitions: NumPartitions
