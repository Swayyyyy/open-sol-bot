import pytest
from solbot_common.constants import WSOL
from solbot_common.utils.utils import calculate_auto_slippage


def test_get_associated_bonding_curve():
    from solbot_common.utils import get_associated_bonding_curve
    from solders.pubkey import Pubkey

    bonding_curve = Pubkey.from_string("4t4o5UATYv1tvBbFU7yte75cGCVLaAA5mWkGdh4cMtzp")
    mint = Pubkey.from_string("AYpgFp9DKcajYo2HuhdtTKcXVD3yjK27oYiHL37Lpump")

    associated_bonding_curve = get_associated_bonding_curve(bonding_curve, mint)
    assert str(associated_bonding_curve) == "BxKK3qTsM3dcM1U5zJi3gVpddDpskkxfL7qgR4G749aU"


@pytest.mark.asyncio
async def test_calculate_auto_slippage():
    input_mint = str(WSOL)
    # output_mint = "5mjE9nom9Hzi4vdTjo862cbbCAhV6JsXMHzwYF2apump"
    output_mint = "GDhVDfnEVtJazEbt43SnFKRGV8ZhMzYZE5hhNcXspump"
    amount = 4900000000
    swap_mode = "ExactIn"
    val = await calculate_auto_slippage(
        input_mint,
        output_mint,
        amount,
        swap_mode,
    )
