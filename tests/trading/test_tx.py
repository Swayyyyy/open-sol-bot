import httpx
import pytest
from solbot_common.config import settings
from solbot_common.constants import WSOL
from solbot_common.utils import get_async_client
from trading.tx import sign_transaction_from_raw


@pytest.mark.asyncio
async def test_sign_transaction_from_raw():
    client = get_async_client()
    params = {
        "token_in_address": "HiPZWtXxEvgzKnMBfHGvZqHfvgaJ1YHZVhwai1Wd8t4J",
        "token_out_address": str(WSOL),
        "in_amount": 10000,
        "from_address": "HyygEkpVJJpuUyUYdAWQTZMwX4Ee1BS9ND7Yd2YdkWQg",
        "slippage": 1,
        "swap_mode": "ExactOut",
        "fee": 0.0001,
    }

    resp = await httpx.AsyncClient(base_url="https://gmgn.ai").get(
        "/defi/router/v1/sol/tx/get_swap_route", params=params
    )
    resp.raise_for_status()

    js = resp.json()
    if js["code"] != 0:
        raise Exception(js["msg"])

    data = js["data"]
    raw_tx = data["raw_tx"]
    swap_tx = raw_tx["swapTransaction"]

    signed_tx = await sign_transaction_from_raw(swap_tx, settings.wallet.keypair)

    resp = await client.simulate_transaction(signed_tx)
    if resp.value.err is not None:
        raise Exception(resp.value.err)

    # resp = await client.send_transaction(signed_tx)
    # print(resp)
