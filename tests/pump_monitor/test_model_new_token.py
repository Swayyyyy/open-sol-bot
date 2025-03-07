from solbot_common.models.new_token import NewToken


def test_new_token_model():
    """Test creating NewToken with alias fields"""
    example = {
        "signature": "4uTy6e7h2SyxuwMyGsJ2Mxh3Rrj99CFeQ6uF1H8xFsEzW8xfrUZ9Xb8QxYutd5zt2cutP45CSPX3CypMAc3ykr2q",
        "mint": "DjmgD4sawByggagUqjxXqs9hAxAXb7Nf76Pzrk9npump",
        "traderPublicKey": "Brw8BKYSkpYtYCmHdhxd61itAw6K4qbcUMJWqm3Ak54z",
        "txType": "create",
        "initialBuy": 0.1,
        "bondingCurveKey": "7tSQHvdKiRQz2YEwk1Lqq2LXBxUgHmYnVwckqWF6kGDP",
        "vTokensInBondingCurve": 1000000.0,
        "vSolInBondingCurve": 10.0,
        "marketCapSol": 10.0,
        "name": "Pump Portal",
        "symbol": "PUMP",
        "uri": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
    }

    new_token = NewToken(**example)

    # 验证所有字段都被正确解析
    assert new_token.signature == example["signature"]
    assert new_token.mint == example["mint"]
    assert new_token.trader_public_key == example["traderPublicKey"]
    assert new_token.tx_type == example["txType"]
    assert new_token.initial_buy == example["initialBuy"]
    assert new_token.bonding_curve_key == example["bondingCurveKey"]
    assert new_token.v_tokens_in_bonding_curve == example["vTokensInBondingCurve"]
    assert new_token.v_sol_in_bonding_curve == example["vSolInBondingCurve"]
    assert new_token.market_cap_sol == example["marketCapSol"]
    assert new_token.name == example["name"]
    assert new_token.symbol == example["symbol"]
    assert new_token.uri == example["uri"]
