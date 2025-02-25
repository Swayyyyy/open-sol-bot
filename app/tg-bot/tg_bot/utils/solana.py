"""Solana-related utility functions."""

import re

from solders.keypair import Keypair  # type: ignore


def validate_solana_address(address: str) -> tuple[bool, str]:
    """
    Validate a Solana wallet address.

    Args:
        address (str): The Solana address to validate

    Returns:
        tuple[bool, str]: A tuple of (is_valid, error_message)
    """
    # Solana addresses are base58 encoded and 32-44 characters long
    base58_pattern = r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"

    # Remove any whitespace
    address = address.strip()

    # Basic format check
    if not re.match(base58_pattern, address):
        return (
            False,
            "无效的 Solana 钱包地址格式。请确保地址是 32-44 个字符的 base58 编码字符串。",
        )

    return True, ""


def validate_solana_private_key(private_key: str) -> tuple[bool, str]:
    """
    Validate a Solana private key.

    Args:
        private_key (str): The Solana private key to validate

    Returns:
        tuple[bool, str]: A tuple of (is_valid, error_message)
    """
    # Solana private keys are base58 encoded and 64 characters long
    base58_pattern = r"^[1-9A-HJ-NP-Za-km-z]{64,88}$"

    # Remove any whitespace
    private_key = private_key.strip()

    # Basic format check
    if not re.match(base58_pattern, private_key):
        return (
            False,
            "无效的 Solana 私钥格式",
        )

    return True, ""


def generate_keypair() -> Keypair:
    """Generate a new Solana keypair.

    Returns:
        Keypair: A Solana keypair object containing both public and private keys
    """
    return Keypair()
