from aiogram import enums

from common.models import TokenInfo
from tg_bot.keyboards.swap import get_token_keyboard
from common.types.bot_setting import BotSetting as Setting
from tg_bot.templates import render_swap_token_message


def render(token_info: TokenInfo, setting: Setting) -> dict:
    text = render_swap_token_message(token_info=token_info, setting=setting)
    keyboard = get_token_keyboard(setting, mint=token_info.mint)
    return {
        "text": text,
        "parse_mode": enums.ParseMode.HTML,
        "reply_markup": keyboard,
        "disable_web_page_preview": True,
    }
