import pytest
from solbot_cache.rayidum import get_preferred_pool


@pytest.mark.asyncio
async def test_get_preferred_pool():
    token_mint = "2ru87k7yAZnDRsnqVpgJYETFgqVApuBcwB2xDb19pump"
    pool = await get_preferred_pool(token_mint)
    assert pool is not None
