import pytest
from solbot_common.utils import validate_transaction


@pytest.mark.asyncio
async def test_validate_transaction():
    tx_hash = (
        "35AkbgknqZ5W8zb4PKuEaf9WmDN9PtwN4Yvcs52hMU3YerRpWMcqZKo6QTu6BHpQC6gxMXxTHijPK17J956HHV38"
    )
    result = await validate_transaction(tx_hash)
    assert result is True


@pytest.mark.asyncio
async def test_validate_transaction_fail_tx_hash():
    tx_hash = (
        "2fL3qiQSVfVt2Vf5PLTepRw7pV5cgiqoLefvHqddUggfAbokEP9TRVGkdBRYa832RrpfX4PoLWfzo61yJDFGuBrt"
    )
    result = await validate_transaction(tx_hash)
    assert result is False
