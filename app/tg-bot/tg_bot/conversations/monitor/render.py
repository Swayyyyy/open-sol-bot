from aiogram import types

from tg_bot.keyboards.monitor import monitor_keyboard_menu
from tg_bot.services.monitor import MonitorService
from tg_bot.templates import render_monitor_menu


async def render(callback: types.CallbackQuery) -> dict:
    s = MonitorService()
    records = await s.list_by_owner(callback.from_user.id)

    text = render_monitor_menu(records)
    keyboard = monitor_keyboard_menu(records)
    return {
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
    }
