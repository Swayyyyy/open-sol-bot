def test_load_config():
    from solbot_common.config import settings

    assert settings.wallet.private_key is not None
    assert settings.rpc.network == "mainnet-beta"
    assert settings.copytrades is not None
