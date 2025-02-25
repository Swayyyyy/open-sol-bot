from anchorpy.program.core import Program
from anchorpy.provider import Provider, Wallet
from anchorpy_core.idl import Idl  # type: ignore
import pathlib

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.instruction import Instruction
from solders.pubkey import Pubkey

from common.constants import (
    EVENT_AUTHORITY,
    PUMP_FUN_PROGRAM,
    RENT_PROGRAM_ID,
    SYSTEM_PROGRAM_ID,
    TOKEN_PROGRAM_ID,
    PUMP_GLOBAL_ACCOUNT,
)


class PumpFunInterface:
    def __init__(self, keypair: Keypair, client: AsyncClient):
        self.keypair = keypair
        self.client = client
        provider = Provider(connection=client, wallet=Wallet(keypair))
        idl_path = pathlib.Path(__file__).parent / "pumpfun.json"
        with open(idl_path) as f:
            idl = Idl.from_json(f.read())

        self.program = Program(idl, PUMP_FUN_PROGRAM, provider)
        self.connection = provider.connection

    def buy(
        self,
        mint: str,
        token_amount: int,
        sol_amount: int,
        buyer: Pubkey,
        fee_recipient: Pubkey,
        bonding_curve_pda: Pubkey,
        associated_bonding_curve: Pubkey,
        ata: Pubkey,
    ) -> Instruction:
        buy_builder = self.program.methods["buy"]

        return (
            buy_builder.args([token_amount, sol_amount])
            .accounts(
                {
                    "fee_recipient": fee_recipient,
                    "mint": mint,
                    "bonding_curve": bonding_curve_pda,
                    "associated_bonding_curve": associated_bonding_curve,
                    "associated_user": ata,
                    "user": buyer,
                    "global": PUMP_GLOBAL_ACCOUNT,
                    "system_program": SYSTEM_PROGRAM_ID,
                    "token_program": TOKEN_PROGRAM_ID,
                    "rent": RENT_PROGRAM_ID,
                    "event_authority": EVENT_AUTHORITY,
                    "program": PUMP_FUN_PROGRAM,
                }
            )
            .instruction()
        )


if __name__ == "__main__":
    from common.utils import get_async_client
    from solders.keypair import Keypair  # type: ignore

    keypair = Keypair()
    wallet = Wallet(keypair)
    client = get_async_client()
    pump_fun = PumpFunInterface(keypair, client)
