import pytest
from solbot_common.utils.helius import HeliusAPI


@pytest.mark.asyncio
async def test_get_parsed_transaction():
    helius_api = HeliusAPI()
    tx_hash = (
        "2ga1sWLxDgRMg1RSaFkdi3kBnSb1VcPfxRGBnku9LkqqHaYAho5Kn5xDkvHLcXXUntD8ski7cutLatQAzCrLgw6g"
    )
    parsed_transaction = await helius_api.get_parsed_transaction(tx_hash)
    assert isinstance(parsed_transaction, list)
    assert len(parsed_transaction) == 1
