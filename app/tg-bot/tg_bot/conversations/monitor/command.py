from aiogram.types import Message
from loguru import logger

from tg_bot.keyboards.monitor import monitor_keyboard_menu
from tg_bot.services.monitor import MonitorService
from tg_bot.templates import render_monitor_menu


async def monitor(message: Message):
    """Handle monitor menu button click"""
    s = MonitorService()
    if message.from_user is None:
        logger.warning("No message found in update")
        return
    records = await s.list_by_owner(message.from_user.id)
    # total = len(records)
    # active_cnt = 0
    # for record in records:
    #     if record.active:
    #         active_cnt += 1

    text = render_monitor_menu(records)
    keyboard = monitor_keyboard_menu(records)
    await message.answer(text, reply_markup=keyboard)
