from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from solbot_common.types.tx import TxEvent


def notify_swap_keyboard(tx_event: TxEvent) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="立即交易",
                    callback_data=f"swap:refresh_{tx_event.mint}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="GMGN",
                    url=f"https://t.me/GMGN_sol_bot?start={tx_event.mint}",
                ),
                InlineKeyboardButton(
                    text="Degoee",
                    url=f"https://t.me/dogeebot_bot?start={tx_event.mint}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="SolTrandingBot",
                    url=f"https://t.me/SolTradingBot?start={tx_event.mint}",
                ),
                InlineKeyboardButton(
                    text="Pepeboost",
                    url=f"https://t.me/pepeboost_sol05_bot?start={tx_event.mint}",
                ),
            ],
        ]
    )
