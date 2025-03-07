import json
from pathlib import Path

import pytest
from solbot_common.types import TxType
from wallet_tracker.parser.raw_tx import RawTXParser


def read_raw_tx(name: str) -> dict:
    path = Path(__file__).parent / "tx_examples" / f"{name}.json"
    with open(path) as f:
        return json.load(f)["result"]


@pytest.mark.parametrize(
    "name,expected_signature,expected_from_amount,expected_from_decimals,expected_to_amount,expected_to_decimals,expected_mint,expected_who,expected_tx_type,expected_program_id",
    [
        (
            "raw/open",
            "PzTWo61tqt483ca24YmkF2MHJRTgWWAQRPHdSWNsNxNQH6JqRb7HNMKErDceQWSZ874aymJ9GZ38qd2UcH3gHB7",
            2087044280,
            9,
            59023574727001,
            6,
            "7LCnGcBjiiaqWMkhTfEEemx5mWdLBHbrgDjCPbTbpump",
            "7DMcENeWGQ9MVqy7jLo54n9ibzH1DQBNtTa7otBsgjnJ",
            TxType.OPEN_POSITION,
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        ),
        (
            "raw/open1",
            "35hGxFdEmx3zezFxQujHPkyKYPQBiJaS6meWxNz7GjRqK2uqzu3TSue4YGNTHKoR3Rqc9QyxZ5gyEX9dykv1iLA9",
            1015764062,
            9,
            27242531851477,
            6,
            "7LCnGcBjiiaqWMkhTfEEemx5mWdLBHbrgDjCPbTbpump",
            "GL3VEiyAZi2Vi2kLbFw4M6Lz4U95vJgH8HT1sN6MvgAT",
            TxType.OPEN_POSITION,
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        ),
        (
            "raw/open2",
            "461m5W5dtJ9wAamkFeApe3y7Sw6mdmHhA4Pnw8XoJCFKbY7i7MfbVeDDCvk3fZZBcbNWxRaY5yn3ckpLZGwc9NvU",
            148930424,
            9,
            4563174234155,
            6,
            "7LCnGcBjiiaqWMkhTfEEemx5mWdLBHbrgDjCPbTbpump",
            "5BAVxxaUS1ykh4A6EqLGxxZLaUH9t7qxtabPYFWSswCd",
            TxType.OPEN_POSITION,
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        ),
        (
            "raw/open3",
            "23uE6fRcher44dM1DbcZsDe4trvooafsTMuvAfG4TzgmbeiYde4ho3HSi5VHkvorSGeyqJi9mpC7NNQYSk5AGCkW",
            2207797,
            9,
            1198591705,
            6,
            "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump",
            "2p7Wxmf57ESSqPZXuhaaWbqfTZY5Wr29Z6YKm2dmUgAi",
            TxType.OPEN_POSITION,
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        ),
        (
            "raw/open4",
            "sxMEDoWXRYTzWkoMsj3vm6jvJFNBnsFjNywRTEaSQACDKSvaPHCXXzDR64GV4Ugx7V11DnQRDYbc2L1un7JLSeM",
            204044280,
            9,
            5780097770783,
            6,
            "E6mwHXeGot8cJHiSVzrQEYuiHjArMThcXbbrEUaXpump",
            "2dV7UHwdooBxowaNTjLALuFJaGeRfgcuP6DkUNysMdpX",
            TxType.OPEN_POSITION,
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        ),
        (
            "raw/reduce",
            "4aYfYr2WXeoWGLuPbjg3ygr5F4C91Nja3kFbEXrMtsFFEQx6SK93dcv5jpGAgWMQvP9gEtd8Miv8gTKBnRZgSBN3",
            4489913189,
            6,
            705000,
            9,
            "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump",
            "6jvYtr9G5WQnKs3cFsFtKmEfkbEnUXFhBKsmZad26QPV",
            TxType.REDUCE_POSITION,
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        ),
        (
            "raw/reduce1",
            "Nhwiq1BafFGprFx2t9K4U5YfE9nZ51JwdVtQmMZ7eeaV3QYwFF389Md2BDGL1bu5xiPaTkfJEMfPztDq45YdBbX",
            11809738065,
            6,
            220604549,
            9,
            "7S37Wv8v9BLQ7bCBTSmCgpCHEb7ae9ZVV7YGwDSepump",
            "7W3oJnw4aMb4LzJ1GR2Qn8Rxe2zAavnCHLoHzy95jgvk",
            TxType.REDUCE_POSITION,
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        ),
        (
            "raw/add",
            "xXtotZuDr5ZLvP6npykq6wTyidETe5ryvuoev7c9Jp7oZPxBEj96WuXtZVsuxTkSwyA9GeJYzDpXvC8sdhVyzLy",
            700032741,
            9,
            36815534629,
            6,
            "7S37Wv8v9BLQ7bCBTSmCgpCHEb7ae9ZVV7YGwDSepump",
            "EnSRdkEvjMmBLPMjsyALJ1E7tUMDb6fYaU4U4zYM9GPg",
            TxType.ADD_POSITION,
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        ),
        (
            "raw/close",
            "21tQnqpMftjcccwwUgjiGayaUAxZWuNPgZwrAXHHX2LSc3EeDBBWrm48KM9oUqpqJjPCQkF4fJoMUUZXwysTs1QT",
            7348085442,
            6,
            137172529,
            9,
            "7S37Wv8v9BLQ7bCBTSmCgpCHEb7ae9ZVV7YGwDSepump",
            "DzUMK8FSwWKmVZh5cxHCMPKpGCg6bTXoVgGMD8kr1QtU",
            TxType.CLOSE_POSITION,
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        ),
        (
            "raw/fail",
            "2PniMp1v8ZgYWksrVPDg87sSz1SBueGzXKCECSUAK6z9BCRXgyD21MAs1FdSeXnw3sMwFHhS5TVeiGgiX5zSgNu9",
            6251953735542,
            6,
            178295225,
            9,
            "3kKVvwSgLKcydFTeEuejpKEDqqGxrrKND7B7W9cApump",
            "2dV7UHwdooBxowaNTjLALuFJaGeRfgcuP6DkUNysMdpX",
            TxType.CLOSE_POSITION,
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        ),
        (
            "raw/fail1",
            "2UpH8fRWjtpyfZhSki1y5zH13QLAHw6Fh5YwW4aJwm57VoqmZXCtuYsb9YjJCEKcaiYWqtQpt14bD21u2hfFFFk3",
            214580413,
            9,
            6259754126787,
            6,
            "ExqTq3rSzY3cQX1fjhfRTdwkM9cC729zqtUzfFFhpump",
            "2dV7UHwdooBxowaNTjLALuFJaGeRfgcuP6DkUNysMdpX",
            TxType.OPEN_POSITION,
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        ),
        (
            "raw/fail2",
            "qNvffNPF4VLyAx5vriLgBT27sUfeRNXqkQ4HuSmjYkVKxmgZD7P9dfj3Q4gigX8H1iLwLmEmhXKbabgybBwCezG",
            17581262315,
            6,
            960069,
            9,
            "CGuP59c51dZxXaVSsz1iqG9U7Smmhd42mEhspe4rpump",
            "9WXBAVFR84XKaPDwfUURwtqK4xRKvFswcRMybPqbVUe3",
            TxType.CLOSE_POSITION,
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        ),
    ],
)
def test_parse_raw_tx(
    name: str,
    expected_signature: str,
    expected_from_amount: int,
    expected_from_decimals: int,
    expected_to_amount: int,
    expected_to_decimals: int,
    expected_mint: str,
    expected_who: str,
    expected_tx_type: TxType,
    expected_program_id: str | None,
):
    tx = read_raw_tx(name)
    parsed = RawTXParser(tx).parse()
    assert parsed is not None
    assert parsed.signature == expected_signature
    assert parsed.from_amount == expected_from_amount
    assert parsed.from_decimals == expected_from_decimals
    assert parsed.to_amount == expected_to_amount
    assert parsed.to_decimals == expected_to_decimals
    assert parsed.mint == expected_mint
    assert parsed.who == expected_who
    assert parsed.tx_type == expected_tx_type
    assert parsed.program_id == expected_program_id
