import math

from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solders.hash import Hash  # type: ignore
from solders.pubkey import Pubkey  # type: ignore
from spl.token.instructions import get_associated_token_address

from cache.account import GlobalAccountCache
from common.layouts.bonding_curve_account import BondingCurveAccount
from common.layouts.global_account import GlobalAccount


def get_client() -> Client:
    """获取 Solana RPC 客户端

    Returns:
        Client: Solana RPC 客户端
    """
    from common.config import settings

    return Client(settings.rpc.rpc_url)


def get_async_client() -> AsyncClient:
    """获取 Solana RPC 客户端

    Returns:
        Client: Solana RPC 客户端
    """
    from common.config import settings

    return AsyncClient(settings.rpc.rpc_url)


def get_associated_bonding_curve(bonding_curve: Pubkey, mint: Pubkey) -> Pubkey:
    """
    This function returns the associated bonding curve for a given bonding curve and mint public key.

    Args:
      bonding_curve (Pubkey): The `bonding_curve` parameter is a public key that represents a specific
    bonding curve program on the blockchain. This bonding curve program is responsible for managing the
    token bonding curve logic, such as buying and selling tokens based on a mathematical formula.
      mint (Pubkey): The `mint` parameter is a public key that represents a token mint. In the context
    of blockchain and cryptocurrency, a mint is responsible for creating new tokens. It is a smart
    contract or program that mints new tokens according to predefined rules and conditions.
    """
    return get_associated_token_address(bonding_curve, mint)


async def get_bonding_curve_pda(mint: Pubkey, program: Pubkey) -> Pubkey:
    return Pubkey.find_program_address([b"bonding-curve", bytes(mint)], program)[0]


async def get_bonding_curve_account(
    client: AsyncClient, mint: Pubkey, program: Pubkey
) -> tuple[Pubkey, Pubkey, BondingCurveAccount] | None:
    bonding_curve = await get_bonding_curve_pda(mint, program)
    associated_bonding_curve = get_associated_token_address(bonding_curve, mint)

    account_info = await client.get_account_info_json_parsed(bonding_curve)
    if account_info is None:
        return None
    value = account_info.value
    if value is None:
        return None
    bonding_curve_account = BondingCurveAccount.from_buffer(bytes(value.data))
    return (bonding_curve, associated_bonding_curve, bonding_curve_account)


async def get_global_account(
    client: AsyncClient, program: Pubkey
) -> GlobalAccount | None:
    return await GlobalAccountCache(client).get(program)


def calculate_with_slippage_buy(amount: int, basis_points: int) -> int:
    """
    The function `calculate_with_slippage_buy` calculates the total amount after applying slippage based
    on the given amount and basis points.

    Args:
      amount (int): The `amount` parameter represents the initial amount of a financial asset you want
    to buy. It is an integer value.
      basis_points (int): Basis points are a unit of measure used in finance to describe the percentage
    change in the value or rate of a financial instrument. One basis point is equal to 0.01% or 1/100th
    of a percent. So, if the basis_points parameter is set to 50,

    Returns:
      The function `calculate_with_slippage_buy` is returning the calculated amount after factoring in
    slippage. It takes two parameters: `amount` (the initial amount) and `basis_points` (the slippage in
    basis points). The function calculates the slippage amount by multiplying the `amount` with
    `basis_points` divided by 10000, then adds it to the
    """
    return math.ceil(amount + (amount * basis_points) / 10000)


def calculate_with_slippage_sell(amount: int, basis_points: int) -> int:
    """
    The function `calculate_with_slippage_sell` calculates the amount after applying slippage for
    selling based on the given amount and basis points.

    Args:
      amount (int): The `amount` parameter represents the initial amount of a financial asset that you
    want to sell.
      basis_points (int): Basis points are a unit of measure used in finance to describe the percentage
    change in the value or rate of a financial instrument. One basis point is equal to one-hundredth of
    a percentage point (0.01%).

    Returns:
      The function `calculate_with_slippage_sell` is returning the calculated amount after applying
    slippage. It calculates the slippage amount by subtracting the product of the amount and basis
    points divided by 10000 from the original amount, and then returns the result after flooring it
    using `math.floor()`.
    """
    return math.floor(amount - (amount * basis_points) / 10000)


# 通过查询数据库，来判断钱包是否存在某个 mint 的 ATA
async def has_ata(client: AsyncClient, wallet: Pubkey, mint: Pubkey) -> bool:
    """This function checks if a wallet contains a specific token mint.

    Args:
      wallet (Pubkey): A public key representing a wallet address.
      mint (Pubkey): The `mint` parameter in the function `has_ata` is of type `Pubkey`. It is
        likely a public key representing a token mint in a blockchain or cryptocurrency context. Mints are
        responsible for creating new tokens and managing the token supply.
    """
    ata_address = get_associated_token_address(wallet, mint)
    resp = await client.get_account_info(ata_address)
    return bool(resp.value) if resp else False


def min_amount_with_slippage(input_amount: int, slippage_bps: int) -> int:
    return input_amount * (10000 - slippage_bps) // 10000


def max_amount_with_slippage(input_amount: int, slippage_bps: int) -> int:
    return input_amount * (10000 + slippage_bps) // 10000


async def get_latest_blockhash(client: AsyncClient) -> Hash:
    # PERF: 应该从 redis 缓存中获取 blockhash
    return (await client.get_latest_blockhash()).value.blockhash


def calc_tx_units(fee: float) -> tuple[int, int]:
    """根据期望的优先费用计算 unit price 和 unit limit

    Args:
        fee: 期望支付的优先费用，单位是 SOL

    Returns:
        tuple[int, int]: (unit_price, unit_limit)
        - unit_price: 每个计算单位的价格（以 micro-lamports 为单位）
        - unit_limit: 交易的计算单位上限
    """
    # 设置固定的计算单位上限
    unit_limit = 200_000

    # 将 SOL 转换为 lamports (1 SOL = 10^9 lamports)
    fee_in_lamports = int(fee * 1e9)

    # 计算每个计算单位的价格
    # 由于 unit_price 是以 micro-lamports 为单位，所以需要再乘以 1e6
    unit_price = int((fee_in_lamports * 1e6) / unit_limit)

    return unit_price, unit_limit


def calc_tx_units_and_split_fees(
    fee: float,
) -> tuple[int, int, float]:
    """根据期望的优先费用计算 unit price 和 unit limit,同时计算 Jito 的小费

    优先费用占比为 70%, Jito 小费占比为 30%,参考https://docs.jito.wtf/lowlatencytxnsend/#id19

    Args:
        fee (float): 总费用，单位是 SOL

    Returns:
        tuple[int, int, float]: (unit_price, unit_limit, jito_fee)
        - unit_price: 每个计算单位的价格（以 micro-lamports 为单位）
        - unit_limit: 交易的计算单位上限
        - jito_fee: Jito 的小费，单位是 SOL
    """
    priority_fee = fee * 0.7
    jito_fee = fee * 0.3
    unit_price, unit_limit = calc_tx_units(priority_fee)
    return unit_price, unit_limit, jito_fee
