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
    account_keys: list[bytes]
    recent_blockhash: bytes
    instructions: list[CompiledInstruction]
    versioned: bool
    address_table_lookups: list[MessageAddressTableLookup]

class Transaction(_Message):
    signatures: list[bytes]
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
    stack_height: int | None

class InnerInstructions(_Message):
    index: int
    instructions: list[InnerInstruction]

class TransactionError(_Message):
    err: bytes

class TransactionStatusMeta(_Message):
    err: TransactionError | None
    fee: int
    pre_balances: list[int]
    post_balances: list[int]
    inner_instructions: list[InnerInstructions]
    inner_instructions_none: bool
    log_messages: list[str]
    log_messages_none: bool
    pre_token_balances: list[TokenBalance]
    post_token_balances: list[TokenBalance]
    rewards: list[Reward]
    loaded_writable_addresses: list[bytes]
    loaded_readonly_addresses: list[bytes]
    return_data: ReturnData | None
    return_data_none: bool
    compute_units_consumed: int | None

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
    rewards: list[Reward]
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
    transactions: list[ConfirmedTransaction]
    rewards: list[Reward]
    block_time: UnixTimestamp
    block_height: BlockHeight
    num_partitions: NumPartitions
