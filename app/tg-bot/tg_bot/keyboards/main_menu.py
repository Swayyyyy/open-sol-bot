from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="💸 买/卖", callback_data="swap"),
            InlineKeyboardButton(text="👥 跟单交易", callback_data="copytrade"),
        ],
        [
            InlineKeyboardButton(text="🔮 我的持仓", callback_data="asset"),
            InlineKeyboardButton(text="🔔 交易监听", callback_data="monitor"),
        ],
        [
            InlineKeyboardButton(text="👛 钱包管理", callback_data="wallet"),
            InlineKeyboardButton(text="⚙️ 设置", callback_data="set"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return reply_markup
