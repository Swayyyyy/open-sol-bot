from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey  # type: ignore
from spl.token.instructions import get_associated_token_address


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
