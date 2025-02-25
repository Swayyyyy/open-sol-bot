from typing import TypedDict

from common.utils import get_associated_token_address, get_async_client
from solders.pubkey import Pubkey  # type: ignore
from spl.token.constants import TOKEN_2022_PROGRAM_ID, TOKEN_PROGRAM_ID  # type: ignore


class TokenAccountBalance(TypedDict):
    amount: int
    decimals: int


async def get_token_account_balance(
    token_mint: str, owner: str
) -> TokenAccountBalance | None:
    """获取 token 余额

    Args:
        rpc_client (AsyncClient): RPC 客户端
        token_mint (str): token 地址
        owner (str): 拥有者地址

    Returns:
        int: 余额，单位 lamports
    """
    rpc_client = get_async_client()
    account = get_associated_token_address(
        Pubkey.from_string(owner), Pubkey.from_string(token_mint), TOKEN_PROGRAM_ID
    )
    resp = await rpc_client.get_token_account_balance(pubkey=account)
    try:
        value = resp.value
        return {
            "amount": int(value.amount),
            "decimals": value.decimals,
        }
    except AttributeError:
        pass

    account = get_associated_token_address(
        Pubkey.from_string(owner),
        Pubkey.from_string(token_mint),
        TOKEN_2022_PROGRAM_ID,
    )
    resp = await rpc_client.get_token_account_balance(pubkey=account)
    try:
        value = resp.value
    except AttributeError:
        return None
    return {
        "amount": int(value.amount),
        "decimals": value.decimals,
    }
