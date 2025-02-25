from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_wallet_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回", callback_data="back_to_home"),
                InlineKeyboardButton(text="🔄 刷新", callback_data="wallet:refresh"),
            ],
            [
                InlineKeyboardButton(text="🆕 更换新钱包", callback_data="wallet:new"),
                InlineKeyboardButton(text="🔐 导出私钥", callback_data="wallet:export"),
            ],
        ]
    )
    return keyboard


def new_wallet_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="导入私钥", callback_data="wallet:import"),
                InlineKeyboardButton(text="🔙 返回", callback_data="wallet:back"),
            ],
        ]
    )
    return keyboard
