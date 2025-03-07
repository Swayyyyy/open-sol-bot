import pytest
from solbot_common.utils.pool import fetch_amm_v4_pool_keys


@pytest.mark.asyncio
async def test_fetch_amm_v4_pool_keys():
    pool_id = "36tmciCKhwQQnyUwWdyHJLoQradFEkhMtJnG8KNJQ1Lw"
    keys = await fetch_amm_v4_pool_keys(pool_id)
    print(keys)
    raise NotImplementedError
