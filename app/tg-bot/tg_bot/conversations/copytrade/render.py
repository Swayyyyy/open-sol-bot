from aiogram import types

from tg_bot.keyboards.copytrade import copytrade_keyboard_menu
from tg_bot.services.copytrade import CopyTradeService
from tg_bot.templates import render_copytrade_menu


async def render(callback: types.CallbackQuery) -> dict:
    s = CopyTradeService()
    records = await s.list_by_owner(callback.from_user.id)
    total = len(records)
    active_cnt = 0
    for record in records:
        if record.active:
            active_cnt += 1

    text = render_copytrade_menu(total, active_cnt)
    keyboard = copytrade_keyboard_menu(records)
    return {
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
    }
