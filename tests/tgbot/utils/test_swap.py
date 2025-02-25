import pytest
from tg_bot.utils.swap import get_token_account_balance


@pytest.mark.asyncio
async def test_get_token_account_balance():
    wallet = "DpAXRS9RpELJmbDtQ657cVvX9wLBnDo1r6Tj3hKdps9"
    token_mint = "znv3FZt2HFAvzYf5LxzVyryh3mBXWuTRRng25gEZAjh"
    balance = await get_token_account_balance(token_mint, wallet)
    assert balance is not None


@pytest.mark.asyncio
async def test_get_token_account_balance_none():
    wallet = "Cwfvqczwmj7B6edeZPwG9iDFoEVwYK2Pcfy7NCYywQ6X"
    token_mint = "znv3FZt2HFAvzYf5LxzVyryh3mBXWuTRRng25gEZAjh"
    balance = await get_token_account_balance(token_mint, wallet)
    assert balance is None
