from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_asset_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回", callback_data="back_to_home"),
                InlineKeyboardButton(text="🔄 刷新", callback_data="asset:refresh"),
            ],
        ]
    )
    return keyboard
