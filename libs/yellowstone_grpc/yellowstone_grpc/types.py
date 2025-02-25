from base64 import b64decode
from enum import IntEnum
from typing import Dict, List, Optional, Union

from base58 import b58decode, b58encode
from pydantic import BaseModel, Field

from .grpc.geyser_pb2 import GetBlockHeightRequest as ProtoGetBlockHeightRequest
from .grpc.geyser_pb2 import GetBlockHeightResponse as ProtoGetBlockHeightResponse
from .grpc.geyser_pb2 import GetLatestBlockhashRequest as ProtoGetLatestBlockhashRequest
from .grpc.geyser_pb2 import (
    GetLatestBlockhashResponse as ProtoGetLatestBlockhashResponse,
)
from .grpc.geyser_pb2 import GetSlotRequest as ProtoGetSlotRequest
from .grpc.geyser_pb2 import GetSlotResponse as ProtoGetSlotResponse
from .grpc.geyser_pb2 import GetVersionRequest as ProtoGetVersionRequest
from .grpc.geyser_pb2 import GetVersionResponse as ProtoGetVersionResponse
from .grpc.geyser_pb2 import IsBlockhashValidRequest as ProtoIsBlockhashValidRequest
from .grpc.geyser_pb2 import IsBlockhashValidResponse as ProtoIsBlockhashValidResponse
from .grpc.geyser_pb2 import PingRequest as ProtoPingRequest
from .grpc.geyser_pb2 import PongResponse as ProtoPongResponse
from .grpc.geyser_pb2 import SubscribeRequest as ProtoRequest
from .grpc.geyser_pb2 import SubscribeRequestAccountsDataSlice as ProtoRequestDataSlice
from .grpc.geyser_pb2 import SubscribeRequestFilterAccounts as ProtoRequestAccounts
from .grpc.geyser_pb2 import SubscribeRequestFilterAccountsFilter as ProtoRequestFilter
from .grpc.geyser_pb2 import (
    SubscribeRequestFilterAccountsFilterLamports as ProtoRequestLamports,
)
from .grpc.geyser_pb2 import (
    SubscribeRequestFilterAccountsFilterMemcmp as ProtoRequestMemcmp,
)
from .grpc.geyser_pb2 import SubscribeRequestFilterBlocks as ProtoRequestBlocks
from .grpc.geyser_pb2 import SubscribeRequestFilterBlocksMeta as ProtoRequestBlocksMeta
from .grpc.geyser_pb2 import SubscribeRequestFilterEntry as ProtoRequestEntry
from .grpc.geyser_pb2 import SubscribeRequestFilterSlots as ProtoRequestSlots
from .grpc.geyser_pb2 import (
    SubscribeRequestFilterTransactions as ProtoRequestTransactions,
)
from .grpc.geyser_pb2 import SubscribeRequestPing as ProtoRequestPing
from .grpc.geyser_pb2 import SubscribeUpdate as ProtoUpdate
from .grpc.geyser_pb2 import SubscribeUpdateAccount as ProtoAccount
from .grpc.geyser_pb2 import SubscribeUpdateAccountInfo as ProtoAccountInfo
from .grpc.geyser_pb2 import SubscribeUpdateBlock as ProtoBlock
from .grpc.geyser_pb2 import SubscribeUpdateBlockMeta as ProtoBlockMeta
from .grpc.geyser_pb2 import SubscribeUpdateEntry as ProtoEntry
from .grpc.geyser_pb2 import SubscribeUpdatePing as ProtoPing
from .grpc.geyser_pb2 import SubscribeUpdatePong as ProtoPong
from .grpc.geyser_pb2 import SubscribeUpdateSlot as ProtoSlot
from .grpc.geyser_pb2 import SubscribeUpdateTransaction as ProtoUpdateTransaction
from .grpc.geyser_pb2 import SubscribeUpdateTransactionInfo as ProtoTransactionInfo
from .grpc.geyser_pb2 import SubscribeUpdateTransactionStatus as ProtoTransactionStatus
from .grpc.solana_storage_pb2 import BlockHeight as ProtoBlockHeight
from .grpc.solana_storage_pb2 import CompiledInstruction as ProtoCompiledInstruction
from .grpc.solana_storage_pb2 import ConfirmedBlock as ProtoConfirmedBlock
from .grpc.solana_storage_pb2 import ConfirmedTransaction as ProtoConfirmedTransaction
from .grpc.solana_storage_pb2 import InnerInstruction as ProtoInnerInstruction
from .grpc.solana_storage_pb2 import InnerInstructions as ProtoInnerInstructions
from .grpc.solana_storage_pb2 import Message as ProtoMessage
from .grpc.solana_storage_pb2 import (
    MessageAddressTableLookup as ProtoMessageAddressTableLookup,
)
from .grpc.solana_storage_pb2 import MessageHeader as ProtoMessageHeader
from .grpc.solana_storage_pb2 import NumPartitions as ProtoNumPartitions
from .grpc.solana_storage_pb2 import ReturnData as ProtoReturnData
from .grpc.solana_storage_pb2 import Reward as ProtoReward
from .grpc.solana_storage_pb2 import Rewards as ProtoRewards
from .grpc.solana_storage_pb2 import TokenBalance as ProtoTokenBalance
from .grpc.solana_storage_pb2 import Transaction as ProtoTransaction
from .grpc.solana_storage_pb2 import TransactionError as ProtoTransactionError
from .grpc.solana_storage_pb2 import TransactionStatusMeta as ProtoTransactionStatusMeta
from .grpc.solana_storage_pb2 import UiTokenAmount as ProtoUiTokenAmount
from .grpc.solana_storage_pb2 import UnixTimestamp as ProtoUnixTimestamp


class CommitmentLevel(IntEnum):
    PROCESSED = 0
    CONFIRMED = 1
    FINALIZED = 2
    FIRST_SHRED_RECEIVED = 3
    COMPLETED = 4
    CREATED_BANK = 5
    DEAD = 6


class SubscribeRequestFilterAccountsFilterMemcmp(BaseModel):
    offset: int
    data: Union[bytes, str] = Field(default=b"")
    data_type: str = Field(default="bytes")  # can be "bytes", "base58", or "base64"

    def get_bytes(self) -> bytes:
        if self.data_type == "bytes":
            return (
                self.data if isinstance(self.data, bytes) else bytes(self.data, "utf-8")
            )
        elif self.data_type == "base58":
            return b58decode(self.data)
        elif self.data_type == "base64":
            return b64decode(self.data)
        raise ValueError(f"Unknown data type: {self.data_type}")

    @classmethod
    def from_proto(
        cls, proto_memcmp: "ProtoRequestMemcmp"
    ) -> "SubscribeRequestFilterAccountsFilterMemcmp":
        return cls(
            offset=proto_memcmp.offset,
            data=proto_memcmp.data,
            data_type=proto_memcmp.data_type,
        )

    def to_proto(self) -> "ProtoRequestMemcmp":
        proto = ProtoRequestMemcmp()
        proto.offset = self.offset
        proto.data = self.data
        proto.data_type = self.data_type
        return proto


class SubscribeRequestFilterAccountsFilterLamports(BaseModel):
    eq: Optional[int] = None
    ne: Optional[int] = None
    lt: Optional[int] = None
    gt: Optional[int] = None

    @classmethod
    def from_proto(
        cls, proto_lamports: "ProtoRequestLamports"
    ) -> "SubscribeRequestFilterAccountsFilterLamports":
        return cls(
            eq=proto_lamports.eq if proto_lamports.HasField("eq") else None,
            ne=proto_lamports.ne if proto_lamports.HasField("ne") else None,
            lt=proto_lamports.lt if proto_lamports.HasField("lt") else None,
            gt=proto_lamports.gt if proto_lamports.HasField("gt") else None,
        )

    def to_proto(self) -> "ProtoRequestLamports":
        proto = ProtoRequestLamports()
        if self.eq is not None:
            proto.eq = self.eq
        if self.ne is not None:
            proto.ne = self.ne
        if self.lt is not None:
            proto.lt = self.lt
        if self.gt is not None:
            proto.gt = self.gt
        return proto


class SubscribeRequestFilterAccountsFilter(BaseModel):
    memcmp: Optional[SubscribeRequestFilterAccountsFilterMemcmp] = None
    datasize: Optional[int] = None
    token_account_state: Optional[bool] = None
    lamports: Optional[SubscribeRequestFilterAccountsFilterLamports] = None

    @classmethod
    def from_proto(
        cls, proto_filter: "ProtoRequestFilter"
    ) -> "SubscribeRequestFilterAccountsFilter":
        return cls(
            memcmp=(
                SubscribeRequestFilterAccountsFilterMemcmp.from_proto(
                    proto_filter.memcmp
                )
                if proto_filter.memcmp is not None
                else None
            ),
            datasize=(
                proto_filter.datasize if proto_filter.HasField("datasize") else None
            ),
            token_account_state=(
                proto_filter.token_account_state
                if proto_filter.HasField("token_account_state")
                else None
            ),
            lamports=(
                SubscribeRequestFilterAccountsFilterLamports.from_proto(
                    proto_filter.lamports
                )
                if proto_filter.lamports is not None
                else None
            ),
        )

    def to_proto(self) -> "ProtoRequestFilter":
        proto = ProtoRequestFilter()
        if self.memcmp:
            proto.memcmp.CopyFrom(self.memcmp.to_proto())
        if self.datasize is not None:
            proto.datasize = self.datasize
        if self.token_account_state is not None:
            proto.token_account_state = self.token_account_state
        if self.lamports:
            proto.lamports.CopyFrom(self.lamports.to_proto())
        return proto


class SubscribeRequestFilterAccounts(BaseModel):
    account: List[str] = Field(default_factory=list)
    owner: List[str] = Field(default_factory=list)
    filters: List[SubscribeRequestFilterAccountsFilter] = Field(default_factory=list)
    nonempty_txn_signature: Optional[bool] = None

    @classmethod
    def from_proto(
        cls, proto_accounts: "ProtoRequestAccounts"
    ) -> "SubscribeRequestFilterAccounts":
        return cls(
            account=list(proto_accounts.account),
            owner=list(proto_accounts.owner),
            filters=[
                SubscribeRequestFilterAccountsFilter.from_proto(f)
                for f in proto_accounts.filters
            ],
            nonempty_txn_signature=(
                proto_accounts.nonempty_txn_signature
                if proto_accounts.HasField("nonempty_txn_signature")
                else None
            ),
        )

    def to_proto(self) -> "ProtoRequestAccounts":
        proto = ProtoRequestAccounts()
        proto.account.extend(self.account)
        proto.owner.extend(self.owner)
        proto.filters.extend([f.to_proto() for f in self.filters])
        if self.nonempty_txn_signature is not None:
            proto.nonempty_txn_signature = self.nonempty_txn_signature
        return proto


class SubscribeRequestFilterSlots(BaseModel):
    filter_by_commitment: Optional[bool] = None

    @classmethod
    def from_proto(
        cls, proto_slots: "ProtoRequestSlots"
    ) -> "SubscribeRequestFilterSlots":
        return cls(
            filter_by_commitment=(
                proto_slots.filter_by_commitment
                if proto_slots.HasField("filter_by_commitment")
                else None
            )
        )

    def to_proto(self) -> "ProtoRequestSlots":
        proto = ProtoRequestSlots()
        if self.filter_by_commitment is not None:
            proto.filter_by_commitment = self.filter_by_commitment
        return proto


class SubscribeRequestFilterTransactions(BaseModel):
    vote: Optional[bool] = None
    failed: Optional[bool] = None
    signature: Optional[str] = None
    account_include: List[str] = Field(default_factory=list)
    account_exclude: List[str] = Field(default_factory=list)
    account_required: List[str] = Field(default_factory=list)

    @classmethod
    def from_proto(
        cls, proto_txns: "ProtoRequestTransactions"
    ) -> "SubscribeRequestFilterTransactions":
        return cls(
            vote=proto_txns.vote if proto_txns.HasField("vote") else None,
            failed=proto_txns.failed if proto_txns.HasField("failed") else None,
            signature=(
                proto_txns.signature if proto_txns.HasField("signature") else None
            ),
            account_include=list(proto_txns.account_include),
            account_exclude=list(proto_txns.account_exclude),
            account_required=list(proto_txns.account_required),
        )

    def to_proto(self) -> "ProtoRequestTransactions":
        proto = ProtoRequestTransactions()
        if self.vote is not None:
            proto.vote = self.vote
        if self.failed is not None:
            proto.failed = self.failed
        if self.signature is not None:
            proto.signature = self.signature
        proto.account_include.extend(self.account_include)
        proto.account_exclude.extend(self.account_exclude)
        proto.account_required.extend(self.account_required)
        return proto


class SubscribeRequestFilterBlocks(BaseModel):
    account_include: List[str] = Field(default_factory=list)
    include_transactions: Optional[bool] = None
    include_accounts: Optional[bool] = None
    include_entries: Optional[bool] = None

    @classmethod
    def from_proto(
        cls, proto_blocks: "ProtoRequestBlocks"
    ) -> "SubscribeRequestFilterBlocks":
        return cls(
            account_include=list(proto_blocks.account_include),
            include_transactions=(
                proto_blocks.include_transactions
                if proto_blocks.HasField("include_transactions")
                else None
            ),
            include_accounts=(
                proto_blocks.include_accounts
                if proto_blocks.HasField("include_accounts")
                else None
            ),
            include_entries=(
                proto_blocks.include_entries
                if proto_blocks.HasField("include_entries")
                else None
            ),
        )

    def to_proto(self) -> "ProtoRequestBlocks":
        proto = ProtoRequestBlocks()
        proto.account_include.extend(self.account_include)
        if self.include_transactions is not None:
            proto.include_transactions = self.include_transactions
        if self.include_accounts is not None:
            proto.include_accounts = self.include_accounts
        if self.include_entries is not None:
            proto.include_entries = self.include_entries
        return proto


class SubscribeRequestFilterBlocksMeta(BaseModel):
    pass


class SubscribeRequestFilterEntry(BaseModel):
    pass


class SubscribeRequestAccountsDataSlice(BaseModel):
    offset: int
    length: int

    @classmethod
    def from_proto(
        cls, proto_slice: "ProtoRequestDataSlice"
    ) -> "SubscribeRequestAccountsDataSlice":
        return cls(offset=proto_slice.offset, length=proto_slice.length)

    def to_proto(self) -> "ProtoRequestDataSlice":
        proto = ProtoRequestDataSlice()
        proto.offset = self.offset
        proto.length = self.length
        return proto


class SubscribeRequestPing(BaseModel):
    id: int

    @classmethod
    def from_proto(cls, proto_ping: "ProtoRequestPing") -> "SubscribeRequestPing":
        return cls(id=proto_ping.id)

    def to_proto(self) -> "ProtoRequestPing":
        return ProtoRequestPing(id=self.id)


class SubscribeRequest(BaseModel):
    accounts: Dict[str, SubscribeRequestFilterAccounts] = Field(default_factory=dict)
    slots: Dict[str, SubscribeRequestFilterSlots] = Field(default_factory=dict)
    transactions: Dict[str, SubscribeRequestFilterTransactions] = Field(
        default_factory=dict
    )
    transactions_status: Dict[str, SubscribeRequestFilterTransactions] = Field(
        default_factory=dict
    )
    blocks: Dict[str, SubscribeRequestFilterBlocks] = Field(default_factory=dict)
    blocks_meta: Dict[str, SubscribeRequestFilterBlocksMeta] = Field(
        default_factory=dict
    )
    entry: Dict[str, SubscribeRequestFilterEntry] = Field(default_factory=dict)
    commitment: Optional[CommitmentLevel] = None
    accounts_data_slice: List[SubscribeRequestAccountsDataSlice] = Field(
        default_factory=list
    )
    ping: Optional[SubscribeRequestPing] = None

    @classmethod
    def from_proto(cls, proto_request: "ProtoRequest") -> "SubscribeRequest":
        return cls(
            accounts={
                k: SubscribeRequestFilterAccounts.from_proto(v)
                for k, v in proto_request.accounts.items()
            },
            slots={
                k: SubscribeRequestFilterSlots.from_proto(v)
                for k, v in proto_request.slots.items()
            },
            transactions={
                k: SubscribeRequestFilterTransactions.from_proto(v)
                for k, v in proto_request.transactions.items()
            },
            transactions_status={
                k: SubscribeRequestFilterTransactions.from_proto(v)
                for k, v in proto_request.transactions_status.items()
            },
            blocks={
                k: SubscribeRequestFilterBlocks.from_proto(v)
                for k, v in proto_request.blocks.items()
            },
            blocks_meta={
                k: SubscribeRequestFilterBlocksMeta()
                for k, v in proto_request.blocks_meta.items()
            },
            entry={
                k: SubscribeRequestFilterEntry() for k, v in proto_request.entry.items()
            },
            commitment=(
                CommitmentLevel(proto_request.commitment)
                if proto_request.HasField("commitment")
                else None
            ),
            accounts_data_slice=[
                SubscribeRequestAccountsDataSlice(
                    offset=slice.offset, length=slice.length
                )
                for slice in proto_request.accounts_data_slice
            ],
            ping=(
                SubscribeRequestPing.from_proto(proto_request.ping)
                if proto_request.ping is not None
                else None
            ),
        )

    def to_proto(self) -> "ProtoRequest":
        proto = ProtoRequest()

        for k, v in self.accounts.items():
            proto.accounts[k].CopyFrom(v.to_proto())
        for k, v in self.slots.items():
            proto.slots[k].CopyFrom(v.to_proto())
        for k, v in self.transactions.items():
            proto.transactions[k].CopyFrom(v.to_proto())
        for k, v in self.transactions_status.items():
            proto.transactions_status[k].CopyFrom(v.to_proto())
        for k, v in self.blocks.items():
            proto.blocks[k].CopyFrom(v.to_proto())
        for k, v in self.blocks_meta.items():
            proto.blocks_meta[k].CopyFrom(ProtoRequestBlocksMeta())
        for k, v in self.entry.items():
            proto.entry[k].CopyFrom(ProtoRequestEntry())

        if self.commitment is not None:
            proto.commitment = self.commitment.value

        for slice in self.accounts_data_slice:
            data_slice = ProtoRequestDataSlice()
            data_slice.offset = slice.offset
            data_slice.length = slice.length
            proto.accounts_data_slice.append(data_slice)

        if self.ping:
            ping = ProtoRequestPing()
            ping.id = self.ping.id
            proto.ping.CopyFrom(ping)

        return proto


from pydantic import field_validator


class SubscribeUpdateAccountInfo(BaseModel):
    pubkey: str
    lamports: int
    owner: str
    executable: bool
    rent_epoch: int
    data: bytes
    write_version: int
    txn_signature: Optional[str] = None

    @field_validator("pubkey", "owner", "txn_signature", mode="before")
    def pubkey_from_str(cls, v: bytes | None) -> str | None:
        if v is None:
            return v
        return b58encode(v).decode("utf-8")

    @classmethod
    def from_proto(
        cls, proto_account: "ProtoAccountInfo"
    ) -> "SubscribeUpdateAccountInfo":
        return cls(
            pubkey=proto_account.pubkey,
            lamports=proto_account.lamports,
            owner=proto_account.owner,
            executable=proto_account.executable,
            rent_epoch=proto_account.rent_epoch,
            data=proto_account.data,
            write_version=proto_account.write_version,
            txn_signature=proto_account.txn_signature,
        )

    def to_proto(self) -> "ProtoAccountInfo":
        proto = ProtoAccountInfo()
        proto.pubkey = self.pubkey
        proto.lamports = self.lamports
        proto.owner = self.owner
        proto.executable = self.executable
        proto.rent_epoch = self.rent_epoch
        proto.data = self.data
        proto.write_version = self.write_version
        if self.txn_signature is not None:
            proto.txn_signature = self.txn_signature
        return proto


class SubscribeUpdateAccount(BaseModel):
    account: SubscribeUpdateAccountInfo
    slot: int
    is_startup: bool

    @classmethod
    def from_proto(cls, proto_account: "ProtoAccount") -> "SubscribeUpdateAccount":
        return cls(
            account=SubscribeUpdateAccountInfo.from_proto(proto_account.account),
            slot=proto_account.slot,
            is_startup=proto_account.is_startup,
        )

    def to_proto(self) -> "ProtoAccount":
        proto = ProtoAccount()
        proto.account.CopyFrom(self.account.to_proto())
        proto.slot = self.slot
        proto.is_startup = self.is_startup
        return proto


class SubscribeUpdateSlot(BaseModel):
    slot: int
    parent: Optional[int] = None
    status: CommitmentLevel = CommitmentLevel.PROCESSED
    dead_error: Optional[str] = None

    @classmethod
    def from_proto(cls, proto_slot: "ProtoSlot") -> "SubscribeUpdateSlot":
        return cls(
            slot=proto_slot.slot,
            parent=proto_slot.parent if proto_slot.HasField("parent") else None,
            status=CommitmentLevel(proto_slot.status),
            dead_error=(
                proto_slot.dead_error if proto_slot.HasField("dead_error") else None
            ),
        )

    def to_proto(self) -> "ProtoSlot":
        proto = ProtoSlot()
        proto.slot = self.slot
        if self.parent is not None:
            proto.parent = self.parent
        proto.status = self.status.value
        if self.dead_error is not None:
            proto.dead_error = self.dead_error
        return proto


class SubscribeUpdateTransactionInfo(BaseModel):
    signature: str
    is_vote: bool
    transaction: "Transaction"
    meta: "TransactionStatusMeta"
    index: int

    @field_validator("signature", mode="before")
    def convert_bytes_to_base58(cls, v: bytes | None) -> str | None:
        if v is None:
            return v
        return b58encode(v).decode("utf-8")

    @classmethod
    def from_proto(
        cls, proto_tx: "ProtoTransactionInfo"
    ) -> "SubscribeUpdateTransactionInfo":
        return cls(
            signature=proto_tx.signature,
            is_vote=proto_tx.is_vote,
            transaction=Transaction.from_proto(proto_tx.transaction),
            meta=TransactionStatusMeta.from_proto(proto_tx.meta),
            index=proto_tx.index,
        )

    def to_proto(self) -> "ProtoTransactionInfo":
        proto = ProtoTransactionInfo()
        proto.signature = self.signature
        proto.is_vote = self.is_vote
        proto.transaction.CopyFrom(self.transaction.to_proto())
        proto.meta.CopyFrom(self.meta.to_proto())
        proto.index = self.index
        return proto


class SubscribeUpdateTransaction(BaseModel):
    transaction: SubscribeUpdateTransactionInfo
    slot: int

    @classmethod
    def from_proto(
        cls, proto_tx: "ProtoUpdateTransaction"
    ) -> "SubscribeUpdateTransaction":
        return cls(
            transaction=SubscribeUpdateTransactionInfo.from_proto(proto_tx.transaction),
            slot=proto_tx.slot,
        )

    def to_proto(self) -> "ProtoUpdateTransaction":
        proto = ProtoUpdateTransaction()
        proto.transaction.CopyFrom(self.transaction.to_proto())
        proto.slot = self.slot
        return proto


class SubscribeUpdateTransactionStatus(BaseModel):
    slot: int
    signature: str
    is_vote: bool
    index: int
    err: "TransactionError"

    @field_validator("signature", mode="before")
    def convert_bytes_to_base58(cls, v: bytes | None) -> str | None:
        if v is None:
            return v
        return b58encode(v).decode("utf-8")

    @classmethod
    def from_proto(
        cls, proto_tx: "ProtoTransactionStatus"
    ) -> "SubscribeUpdateTransactionStatus":
        return cls(
            slot=proto_tx.slot,
            signature=proto_tx.signature,
            is_vote=proto_tx.is_vote,
            index=proto_tx.index,
            err=TransactionError.from_proto(proto_tx.err),
        )

    def to_proto(self) -> "ProtoTransactionStatus":
        proto = ProtoTransactionStatus()
        proto.slot = self.slot
        proto.signature = self.signature
        proto.is_vote = self.is_vote
        proto.index = self.index
        proto.err.CopyFrom(self.err.to_proto())
        return proto


class SubscribeUpdateEntry(BaseModel):
    slot: int
    index: int
    num_hashes: int
    hash: str
    executed_transaction_count: int
    starting_transaction_index: int

    @field_validator("hash", mode="before")
    def convert_bytes_to_base58(cls, v: bytes | None) -> str | None:
        if v is None:
            return v
        return b58encode(v).decode("utf-8")

    @classmethod
    def from_proto(cls, proto_entry: "ProtoEntry") -> "SubscribeUpdateEntry":
        return cls(
            slot=proto_entry.slot,
            index=proto_entry.index,
            num_hashes=proto_entry.num_hashes,
            hash=proto_entry.hash,
            executed_transaction_count=proto_entry.executed_transaction_count,
            starting_transaction_index=proto_entry.starting_transaction_index,
        )

    def to_proto(self) -> "ProtoEntry":
        proto = ProtoEntry()
        proto.slot = self.slot
        proto.index = self.index
        proto.num_hashes = self.num_hashes
        proto.hash = self.hash
        proto.executed_transaction_count = self.executed_transaction_count
        proto.starting_transaction_index = self.starting_transaction_index
        return proto


class SubscribeUpdateBlock(BaseModel):
    slot: int
    blockhash: str
    rewards: list["Reward"]
    block_time: "UnixTimestamp"
    block_height: "BlockHeight"
    parent_slot: int
    parent_blockhash: str
    executed_transaction_count: int
    transactions: List[SubscribeUpdateTransactionInfo] = Field(default_factory=list)
    updated_account_count: int = 0
    accounts: List[SubscribeUpdateAccountInfo] = Field(default_factory=list)
    entries_count: int = 0
    entries: List[SubscribeUpdateEntry] = Field(default_factory=list)

    @classmethod
    def from_proto(cls, proto_block: "ProtoBlock") -> "SubscribeUpdateBlock":
        return cls(
            slot=proto_block.slot,
            blockhash=proto_block.blockhash,
            rewards=[Reward.from_proto(reward) for reward in proto_block.rewards],
            block_time=UnixTimestamp.from_proto(proto_block.block_time),
            block_height=BlockHeight.from_proto(proto_block.block_height),
            parent_slot=proto_block.parent_slot,
            parent_blockhash=proto_block.parent_blockhash,
            executed_transaction_count=proto_block.executed_transaction_count,
            transactions=[
                SubscribeUpdateTransactionInfo.from_proto(tx)
                for tx in proto_block.transactions
            ],
            updated_account_count=proto_block.updated_account_count,
            accounts=[
                SubscribeUpdateAccountInfo.from_proto(account)
                for account in proto_block.accounts
            ],
            entries_count=proto_block.entries_count,
            entries=[
                SubscribeUpdateEntry.from_proto(entry) for entry in proto_block.entries
            ],
        )

    def to_proto(self) -> "ProtoBlock":
        proto = ProtoBlock()
        proto.slot = self.slot
        proto.blockhash = self.blockhash
        proto.rewards.extend([reward.to_proto() for reward in self.rewards])
        proto.block_time.CopyFrom(self.block_time.to_proto())
        proto.block_height.CopyFrom(self.block_height.to_proto())
        proto.parent_slot = self.parent_slot
        proto.parent_blockhash = self.parent_blockhash
        proto.executed_transaction_count = self.executed_transaction_count
        for tx in self.transactions:
            proto.transactions.append(tx.to_proto())
        proto.updated_account_count = self.updated_account_count
        for account in self.accounts:
            proto.accounts.append(account.to_proto())
        proto.entries_count = self.entries_count
        for entry in self.entries:
            proto.entries.append(entry.to_proto())
        return proto


class SubscribeUpdateBlockMeta(BaseModel):
    slot: int
    blockhash: str
    rewards: list["Reward"]
    block_time: "UnixTimestamp"
    block_height: "BlockHeight"
    parent_slot: int
    parent_blockhash: str
    executed_transaction_count: int
    entries_count: int

    @classmethod
    def from_proto(cls, proto_block: "ProtoBlockMeta") -> "SubscribeUpdateBlockMeta":
        return cls(
            slot=proto_block.slot,
            blockhash=proto_block.blockhash,
            rewards=[Reward.from_proto(reward) for reward in proto_block.rewards],
            block_time=UnixTimestamp.from_proto(proto_block.block_time),
            block_height=BlockHeight.from_proto(proto_block.block_height),
            parent_slot=proto_block.parent_slot,
            parent_blockhash=proto_block.parent_blockhash,
            executed_transaction_count=proto_block.executed_transaction_count,
            entries_count=proto_block.entries_count,
        )

    def to_proto(self) -> "ProtoBlockMeta":
        proto = ProtoBlockMeta()
        proto.slot = self.slot
        proto.blockhash = self.blockhash
        proto.rewards.extend([reward.to_proto() for reward in self.rewards])
        proto.block_time.CopyFrom(self.block_time.to_proto())
        proto.block_height.CopyFrom(self.block_height.to_proto())
        proto.parent_slot = self.parent_slot
        proto.parent_blockhash = self.parent_blockhash
        proto.executed_transaction_count = self.executed_transaction_count
        proto.entries_count = self.entries_count
        return proto


class SubscribeUpdatePing(BaseModel):
    @classmethod
    def from_proto(cls, proto_ping: "ProtoPing") -> "SubscribeUpdatePing":
        return cls()

    def to_proto(self) -> "ProtoPing":
        proto = ProtoPing()
        return proto


class SubscribeUpdatePong(BaseModel):
    id: int

    @classmethod
    def from_proto(cls, proto_pong: "ProtoPong") -> "SubscribeUpdatePong":
        return cls(id=proto_pong.id)

    def to_proto(self) -> "ProtoPong":
        proto = ProtoPong()
        proto.id = self.id
        return proto


class SubscribeUpdate(BaseModel):
    filters: List[str] = Field(default_factory=list)
    account: Optional[SubscribeUpdateAccount] = None
    slot: Optional[SubscribeUpdateSlot] = None
    transaction: Optional[SubscribeUpdateTransaction] = None
    transaction_status: Optional[SubscribeUpdateTransactionStatus] = None
    block: Optional[SubscribeUpdateBlock] = None
    block_meta: Optional[SubscribeUpdateBlockMeta] = None
    entry: Optional[SubscribeUpdateEntry] = None
    ping: Optional[SubscribeUpdatePing] = None
    pong: Optional[SubscribeUpdatePong] = None

    @classmethod
    def from_proto(cls, proto_update: "ProtoUpdate") -> "SubscribeUpdate":
        return cls(
            filters=proto_update.filters,
            account=(
                SubscribeUpdateAccount.from_proto(proto_update.account)
                if proto_update.HasField("account") and proto_update.account is not None
                else None
            ),
            slot=(
                SubscribeUpdateSlot.from_proto(proto_update.slot)
                if proto_update.HasField("slot") and proto_update.slot is not None
                else None
            ),
            transaction=(
                SubscribeUpdateTransaction.from_proto(proto_update.transaction)
                if proto_update.HasField("transaction")
                and proto_update.transaction is not None
                else None
            ),
            transaction_status=(
                SubscribeUpdateTransactionStatus.from_proto(
                    proto_update.transaction_status
                )
                if proto_update.HasField("transaction_status")
                and proto_update.transaction_status is not None
                else None
            ),
            block=(
                SubscribeUpdateBlock.from_proto(proto_update.block)
                if proto_update.HasField("block") and proto_update.block is not None
                else None
            ),
            block_meta=(
                SubscribeUpdateBlockMeta.from_proto(proto_update.block_meta)
                if proto_update.HasField("block_meta")
                and proto_update.block_meta is not None
                else None
            ),
            entry=(
                SubscribeUpdateEntry.from_proto(proto_update.entry)
                if proto_update.HasField("entry") and proto_update.entry is not None
                else None
            ),
            ping=(
                SubscribeUpdatePing.from_proto(proto_update.ping)
                if proto_update.HasField("ping") and proto_update.ping is not None
                else None
            ),
            pong=(
                SubscribeUpdatePong.from_proto(proto_update.pong)
                if proto_update.HasField("pong") and proto_update.pong is not None
                else None
            ),
        )

    def to_proto(self) -> "ProtoUpdate":
        proto = ProtoUpdate()
        proto.filters = self.filters
        if self.account is not None:
            proto.account.CopyFrom(self.account.to_proto())
        if self.slot is not None:
            proto.slot.CopyFrom(self.slot.to_proto())
        if self.transaction is not None:
            proto.transaction.CopyFrom(self.transaction.to_proto())
        if self.transaction_status is not None:
            proto.transaction_status.CopyFrom(self.transaction_status.to_proto())
        if self.block is not None:
            proto.block.CopyFrom(self.block.to_proto())
        if self.block_meta is not None:
            proto.block_meta.CopyFrom(self.block_meta.to_proto())
        if self.entry is not None:
            proto.entry.CopyFrom(self.entry.to_proto())
        if self.ping is not None:
            proto.ping.CopyFrom(self.ping.to_proto())
        if self.pong is not None:
            proto.pong.CopyFrom(self.pong.to_proto())
        return proto


class PingRequest(BaseModel):
    count: int

    def to_proto(self) -> "ProtoPingRequest":
        proto = ProtoPingRequest()
        proto.count = self.count
        return proto

    @classmethod
    def from_proto(cls, proto_ping: "ProtoPingRequest") -> "PingRequest":
        return cls(count=proto_ping.count)


class PongResponse(BaseModel):
    count: int

    @classmethod
    def from_proto(cls, proto_pong: "ProtoPongResponse") -> "PongResponse":
        return cls(count=proto_pong.count)

    def to_proto(self) -> "ProtoPongResponse":
        proto = ProtoPongResponse()
        proto.count = self.count
        return proto


class GetLatestBlockhashRequest(BaseModel):
    commitment: Optional[CommitmentLevel] = None

    @classmethod
    def from_proto(
        cls, proto_request: "ProtoGetLatestBlockhashRequest"
    ) -> "GetLatestBlockhashRequest":
        return cls(commitment=CommitmentLevel(proto_request.commitment))

    def to_proto(self) -> "ProtoGetLatestBlockhashRequest":
        proto = ProtoGetLatestBlockhashRequest()
        proto.commitment = self.commitment.value if self.commitment else None
        return proto


class GetLatestBlockhashResponse(BaseModel):
    slot: int
    blockhash: str
    last_valid_block_height: int

    @classmethod
    def from_proto(
        cls, proto_response: "ProtoGetLatestBlockhashResponse"
    ) -> "GetLatestBlockhashResponse":
        return cls(
            slot=proto_response.slot,
            blockhash=proto_response.blockhash,
            last_valid_block_height=proto_response.last_valid_block_height,
        )

    def to_proto(self) -> "ProtoGetLatestBlockhashResponse":
        proto = ProtoGetLatestBlockhashResponse()
        proto.slot = self.slot
        proto.blockhash = self.blockhash
        proto.last_valid_block_height = self.last_valid_block_height
        return proto


class GetBlockHeightRequest(BaseModel):
    commitment: Optional[CommitmentLevel] = None

    @classmethod
    def from_proto(
        cls, proto_request: "ProtoGetBlockHeightRequest"
    ) -> "GetBlockHeightRequest":
        return cls(commitment=CommitmentLevel(proto_request.commitment))

    def to_proto(self) -> "ProtoGetBlockHeightRequest":
        proto = ProtoGetBlockHeightRequest()
        proto.commitment = self.commitment.value if self.commitment else None
        return proto


class GetBlockHeightResponse(BaseModel):
    block_height: int

    @classmethod
    def from_proto(
        cls, proto_response: "ProtoGetBlockHeightResponse"
    ) -> "GetBlockHeightResponse":
        return cls(block_height=proto_response.block_height)

    def to_proto(self) -> "ProtoGetBlockHeightResponse":
        proto = ProtoGetBlockHeightResponse()
        proto.block_height = self.block_height
        return proto


class GetSlotRequest(BaseModel):
    commitment: Optional[CommitmentLevel] = None

    @classmethod
    def from_proto(cls, proto_request: "ProtoGetSlotRequest") -> "GetSlotRequest":
        return cls(commitment=CommitmentLevel(proto_request.commitment))

    def to_proto(self) -> "ProtoGetSlotRequest":
        proto = ProtoGetSlotRequest()
        proto.commitment = self.commitment.value if self.commitment else None
        return proto


class GetSlotResponse(BaseModel):
    slot: int

    @classmethod
    def from_proto(cls, proto_response: "ProtoGetSlotResponse") -> "GetSlotResponse":
        return cls(slot=proto_response.slot)

    def to_proto(self) -> "ProtoGetSlotResponse":
        proto = ProtoGetSlotResponse()
        proto.slot = self.slot
        return proto


class GetVersionRequest(BaseModel):
    @classmethod
    def from_proto(cls, proto_request: "ProtoGetVersionRequest") -> "GetVersionRequest":
        return cls()

    def to_proto(self) -> "ProtoGetVersionRequest":
        proto = ProtoGetVersionRequest()
        return proto


class GetVersionResponse(BaseModel):
    version: str

    @classmethod
    def from_proto(
        cls, proto_response: "ProtoGetVersionResponse"
    ) -> "GetVersionResponse":
        return cls(version=proto_response.version)

    def to_proto(self) -> "ProtoGetVersionResponse":
        proto = ProtoGetVersionResponse()
        proto.version = self.version
        return proto


class IsBlockhashValidRequest(BaseModel):
    blockhash: str
    commitment: Optional[CommitmentLevel] = None

    @classmethod
    def from_proto(
        cls, proto_request: "ProtoIsBlockhashValidRequest"
    ) -> "IsBlockhashValidRequest":
        return cls(
            blockhash=proto_request.blockhash,
            commitment=CommitmentLevel(proto_request.commitment),
        )

    def to_proto(self) -> "ProtoIsBlockhashValidRequest":
        proto = ProtoIsBlockhashValidRequest()
        proto.blockhash = self.blockhash
        proto.commitment = self.commitment.value if self.commitment else None
        return proto


class IsBlockhashValidResponse(BaseModel):
    slot: int
    valid: bool

    @classmethod
    def from_proto(
        cls, proto_response: "ProtoIsBlockhashValidResponse"
    ) -> "IsBlockhashValidResponse":
        return cls(slot=proto_response.slot, valid=proto_response.valid)

    def to_proto(self) -> "ProtoIsBlockhashValidResponse":
        proto = ProtoIsBlockhashValidResponse()
        proto.slot = self.slot
        proto.valid = self.valid
        return proto


# Solana Storage Types
class RewardType(IntEnum):
    Unspecified = 0
    Fee = 1
    Rent = 2
    Staking = 3
    Voting = 4


class MessageHeader(BaseModel):
    num_required_signatures: int
    num_readonly_signed_accounts: int
    num_readonly_unsigned_accounts: int

    @classmethod
    def from_proto(cls, header: "ProtoMessageHeader") -> "MessageHeader":
        return cls(
            num_required_signatures=header.num_required_signatures,
            num_readonly_signed_accounts=header.num_readonly_signed_accounts,
            num_readonly_unsigned_accounts=header.num_readonly_unsigned_accounts,
        )

    def to_proto(self) -> "ProtoMessageHeader":
        proto = ProtoMessageHeader()
        proto.num_required_signatures = self.num_required_signatures
        proto.num_readonly_signed_accounts = self.num_readonly_signed_accounts
        proto.num_readonly_unsigned_accounts = self.num_readonly_unsigned_accounts
        return proto


class MessageAddressTableLookup(BaseModel):
    account_key: str
    writable_indexes: bytes
    readonly_indexes: bytes

    @field_validator("account_key", mode="before")
    def convert_bytes_to_base58(cls, v: bytes | None) -> str | None:
        if v is None:
            return v
        return b58encode(v).decode("utf-8")

    @classmethod
    def from_proto(
        cls, lookup: "ProtoMessageAddressTableLookup"
    ) -> "MessageAddressTableLookup":
        return cls(
            account_key=lookup.account_key,  # type: ignore
            writable_indexes=lookup.writable_indexes,
            readonly_indexes=lookup.readonly_indexes,
        )

    def to_proto(self) -> "ProtoMessageAddressTableLookup":
        proto = ProtoMessageAddressTableLookup()
        proto.account_key = b58decode(self.account_key)
        proto.writable_indexes = self.writable_indexes
        proto.readonly_indexes = self.readonly_indexes
        return proto


class Message(BaseModel):
    header: MessageHeader
    account_keys: List[bytes]
    recent_blockhash: bytes
    instructions: List["CompiledInstruction"]
    versioned: bool
    address_table_lookups: List[MessageAddressTableLookup]

    @classmethod
    def from_proto(cls, proto_message: "ProtoMessage") -> "Message":
        return cls(
            header=MessageHeader.from_proto(proto_message.header),
            account_keys=proto_message.account_keys,
            recent_blockhash=proto_message.recent_blockhash,
            instructions=[
                CompiledInstruction.from_proto(instruction)
                for instruction in proto_message.instructions
            ],
            versioned=proto_message.versioned,
            address_table_lookups=[
                MessageAddressTableLookup.from_proto(lookup)
                for lookup in proto_message.address_table_lookups
            ],
        )

    def to_proto(self) -> "ProtoMessage":
        proto = ProtoMessage()
        proto.header = self.header.to_proto()
        proto.account_keys = self.account_keys
        proto.recent_blockhash = self.recent_blockhash
        proto.instructions = [
            instruction.to_proto() for instruction in self.instructions
        ]
        proto.versioned = self.versioned
        proto.address_table_lookups = [
            lookup.to_proto() for lookup in self.address_table_lookups
        ]
        return proto


class Transaction(BaseModel):
    signatures: List[bytes]
    message: Message

    @classmethod
    def from_proto(cls, proto_transaction: "ProtoTransaction") -> "Transaction":
        return cls(
            signatures=proto_transaction.signatures,
            message=Message.from_proto(proto_transaction.message),
        )

    def to_proto(self) -> "ProtoTransaction":
        proto = ProtoTransaction()
        proto.signatures = self.signatures
        proto.message = self.message.to_proto()
        return proto


class UiTokenAmount(BaseModel):
    ui_amount: float
    decimals: int
    amount: str
    ui_amount_string: str

    @classmethod
    def from_proto(cls, proto_amount: "ProtoUiTokenAmount") -> "UiTokenAmount":
        return cls(
            ui_amount=proto_amount.ui_amount,
            decimals=proto_amount.decimals,
            amount=proto_amount.amount,
            ui_amount_string=proto_amount.ui_amount_string,
        )

    def to_proto(self) -> "ProtoUiTokenAmount":
        proto = ProtoUiTokenAmount()
        proto.ui_amount = self.ui_amount
        proto.decimals = self.decimals
        proto.amount = self.amount
        proto.ui_amount_string = self.ui_amount_string
        return proto


class TokenBalance(BaseModel):
    account_index: int
    mint: str
    ui_token_amount: UiTokenAmount
    owner: str
    program_id: str

    @classmethod
    def from_proto(cls, proto_balance: "ProtoTokenBalance") -> "TokenBalance":
        return cls(
            account_index=proto_balance.account_index,
            mint=proto_balance.mint,
            ui_token_amount=UiTokenAmount.from_proto(proto_balance.ui_token_amount),
            owner=proto_balance.owner,
            program_id=proto_balance.program_id,
        )

    def to_proto(self) -> "ProtoTokenBalance":
        proto = ProtoTokenBalance()
        proto.account_index = self.account_index
        proto.mint = self.mint
        proto.ui_token_amount = self.ui_token_amount.to_proto()
        proto.owner = self.owner
        proto.program_id = self.program_id
        return proto


class ReturnData(BaseModel):
    program_id: bytes
    data: bytes

    @classmethod
    def from_proto(cls, proto_data: "ProtoReturnData") -> "ReturnData":
        return cls(program_id=proto_data.program_id, data=proto_data.data)

    def to_proto(self) -> "ProtoReturnData":
        proto = ProtoReturnData()
        proto.program_id = self.program_id
        proto.data = self.data
        return proto


class CompiledInstruction(BaseModel):
    program_id_index: int
    accounts: bytes
    data: bytes

    @classmethod
    def from_proto(
        cls, proto_instruction: "ProtoCompiledInstruction"
    ) -> "CompiledInstruction":
        return cls(
            program_id_index=proto_instruction.program_id_index,
            accounts=proto_instruction.accounts,
            data=proto_instruction.data,
        )

    def to_proto(self) -> "ProtoCompiledInstruction":
        proto = ProtoCompiledInstruction()
        proto.program_id_index = self.program_id_index
        proto.accounts = self.accounts
        proto.data = self.data
        return proto


class InnerInstruction(BaseModel):
    program_id_index: int
    accounts: bytes
    data: bytes
    stack_height: Optional[int] = None

    @classmethod
    def from_proto(
        cls, proto_instruction: "ProtoInnerInstruction"
    ) -> "InnerInstruction":
        return cls(
            program_id_index=proto_instruction.program_id_index,
            accounts=proto_instruction.accounts,
            data=proto_instruction.data,
            stack_height=proto_instruction.stack_height,
        )

    def to_proto(self) -> "ProtoInnerInstruction":
        proto = ProtoInnerInstruction()
        proto.program_id_index = self.program_id_index
        proto.accounts = self.accounts
        proto.data = self.data
        proto.stack_height = self.stack_height
        return proto


class InnerInstructions(BaseModel):
    index: int
    instructions: List[InnerInstruction]

    @classmethod
    def from_proto(
        cls, proto_instruction: "ProtoInnerInstructions"
    ) -> "InnerInstructions":
        return cls(
            index=proto_instruction.index,
            instructions=[
                InnerInstruction.from_proto(instruction)
                for instruction in proto_instruction.instructions
            ],
        )

    def to_proto(self) -> "ProtoInnerInstructions":
        proto = ProtoInnerInstructions()
        proto.index = self.index
        proto.instructions = [
            instruction.to_proto() for instruction in self.instructions
        ]
        return proto


class TransactionError(BaseModel):
    err: bytes

    @classmethod
    def from_proto(cls, proto_error: "ProtoTransactionError") -> "TransactionError":
        return cls(err=proto_error.err)

    def to_proto(self) -> "ProtoTransactionError":
        proto = ProtoTransactionError()
        proto.err = self.err
        return proto


class TransactionStatusMeta(BaseModel):
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
    compute_units_consumed: Optional[int] = None

    @classmethod
    def from_proto(
        cls, proto_meta: "ProtoTransactionStatusMeta"
    ) -> "TransactionStatusMeta":
        return cls(
            err=TransactionError.from_proto(proto_meta.err) if proto_meta.err else None,
            fee=proto_meta.fee,
            pre_balances=proto_meta.pre_balances,
            post_balances=proto_meta.post_balances,
            inner_instructions=[
                InnerInstructions.from_proto(instruction)
                for instruction in proto_meta.inner_instructions
            ],
            inner_instructions_none=proto_meta.inner_instructions_none,
            log_messages=proto_meta.log_messages,
            log_messages_none=proto_meta.log_messages_none,
            pre_token_balances=[
                TokenBalance.from_proto(balance)
                for balance in proto_meta.pre_token_balances
            ],
            post_token_balances=[
                TokenBalance.from_proto(balance)
                for balance in proto_meta.post_token_balances
            ],
            rewards=[Reward.from_proto(reward) for reward in proto_meta.rewards],
            loaded_writable_addresses=proto_meta.loaded_writable_addresses,
            loaded_readonly_addresses=proto_meta.loaded_readonly_addresses,
            return_data=(
                ReturnData.from_proto(proto_meta.return_data)
                if proto_meta.return_data
                else None
            ),
            return_data_none=proto_meta.return_data_none,
            compute_units_consumed=proto_meta.compute_units_consumed,
        )

    def to_proto(self) -> "ProtoTransactionStatusMeta":
        proto = ProtoTransactionStatusMeta()
        proto.err = self.err.to_proto() if self.err else None
        proto.fee = self.fee
        proto.pre_balances = self.pre_balances
        proto.post_balances = self.post_balances
        proto.inner_instructions = [
            instruction.to_proto() for instruction in self.inner_instructions
        ]
        proto.inner_instructions_none = self.inner_instructions_none
        proto.log_messages = self.log_messages
        proto.log_messages_none = self.log_messages_none
        proto.pre_token_balances = [
            balance.to_proto() for balance in self.pre_token_balances
        ]
        proto.post_token_balances = [
            balance.to_proto() for balance in self.post_token_balances
        ]
        proto.rewards = [reward.to_proto() for reward in self.rewards]
        proto.loaded_writable_addresses = self.loaded_writable_addresses
        proto.loaded_readonly_addresses = self.loaded_readonly_addresses
        proto.return_data = self.return_data.to_proto() if self.return_data else None
        proto.return_data_none = self.return_data_none
        proto.compute_units_consumed = self.compute_units_consumed
        return proto


class ConfirmedTransaction(BaseModel):
    transaction: Transaction
    meta: TransactionStatusMeta

    @classmethod
    def from_proto(
        cls, proto_transaction: "ProtoConfirmedTransaction"
    ) -> "ConfirmedTransaction":
        print(proto_transaction)
        return cls(
            transaction=Transaction.from_proto(proto_transaction.transaction),
            meta=TransactionStatusMeta.from_proto(proto_transaction.meta),
        )

    def to_proto(self) -> "ProtoConfirmedTransaction":
        proto = ProtoConfirmedTransaction()
        proto.transaction = self.transaction.to_proto()
        proto.meta = self.meta.to_proto()
        return proto


class Reward(BaseModel):
    pubkey: str
    lamports: int
    post_balance: int
    reward_type: RewardType
    commission: str

    @classmethod
    def from_proto(cls, proto_reward: "ProtoReward") -> "Reward":
        return cls(
            pubkey=proto_reward.pubkey,
            lamports=proto_reward.lamports,
            post_balance=proto_reward.post_balance,
            reward_type=RewardType(proto_reward.reward_type),
            commission=proto_reward.commission,
        )

    def to_proto(self) -> "ProtoReward":
        proto = ProtoReward()
        proto.pubkey = self.pubkey
        proto.lamports = self.lamports
        proto.post_balance = self.post_balance
        proto.reward_type = self.reward_type
        proto.commission = self.commission
        return proto


class Rewards(BaseModel):
    rewards: List[Reward]
    num_partitions: "NumPartitions"

    @classmethod
    def from_proto(cls, proto_rewards: "ProtoRewards") -> "Rewards":
        return cls(
            rewards=[Reward.from_proto(reward) for reward in proto_rewards.rewards],
            num_partitions=NumPartitions.from_proto(proto_rewards.num_partitions),
        )

    def to_proto(self) -> "ProtoRewards":
        proto = ProtoRewards()
        proto.rewards = [reward.to_proto() for reward in self.rewards]
        proto.num_partitions = self.num_partitions.to_proto()
        return proto


class UnixTimestamp(BaseModel):
    timestamp: int

    @classmethod
    def from_proto(cls, proto_timestamp: "ProtoUnixTimestamp") -> "UnixTimestamp":
        return cls(timestamp=proto_timestamp.timestamp)

    def to_proto(self) -> "ProtoUnixTimestamp":
        proto = ProtoUnixTimestamp()
        proto.timestamp = self.timestamp
        return proto


class BlockHeight(BaseModel):
    block_height: int

    @classmethod
    def from_proto(cls, proto_block_height: "ProtoBlockHeight") -> "BlockHeight":
        return cls(block_height=proto_block_height.block_height)

    def to_proto(self) -> "ProtoBlockHeight":
        proto = ProtoBlockHeight()
        proto.block_height = self.block_height
        return proto


class NumPartitions(BaseModel):
    num_partitions: int

    @classmethod
    def from_proto(cls, proto_num_partitions: "ProtoNumPartitions") -> "NumPartitions":
        return cls(num_partitions=proto_num_partitions.num_partitions)

    def to_proto(self) -> "ProtoNumPartitions":
        proto = ProtoNumPartitions()
        proto.num_partitions = self.num_partitions
        return proto


class ConfirmedBlock(BaseModel):
    previous_blockhash: str
    blockhash: str
    parent_slot: int
    transactions: List[ConfirmedTransaction]
    rewards: List[Reward]
    block_time: UnixTimestamp
    block_height: BlockHeight
    num_partitions: NumPartitions

    @classmethod
    def from_proto(cls, proto_block: "ProtoConfirmedBlock") -> "ConfirmedBlock":
        return cls(
            previous_blockhash=proto_block.previous_blockhash,
            blockhash=proto_block.blockhash,
            parent_slot=proto_block.parent_slot,
            transactions=[
                ConfirmedTransaction.from_proto(transaction)
                for transaction in proto_block.transactions
            ],
            rewards=[Reward.from_proto(reward) for reward in proto_block.rewards],
            block_time=UnixTimestamp.from_proto(proto_block.block_time),
            block_height=BlockHeight.from_proto(proto_block.block_height),
            num_partitions=NumPartitions.from_proto(proto_block.num_partitions),
        )

    def to_proto(self) -> "ProtoConfirmedBlock":
        proto = ProtoConfirmedBlock()
        proto.previous_blockhash = self.previous_blockhash
        proto.blockhash = self.blockhash
        proto.parent_slot = self.parent_slot
        proto.transactions = [
            transaction.to_proto() for transaction in self.transactions
        ]
        proto.rewards = [reward.to_proto() for reward in self.rewards]
        proto.block_time = self.block_time.to_proto()
        proto.block_height = self.block_height.to_proto()
        proto.num_partitions = self.num_partitions.to_proto()
        return proto
