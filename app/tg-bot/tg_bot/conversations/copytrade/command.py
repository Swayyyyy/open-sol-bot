from aiogram import Router
from aiogram.types import Message
from loguru import logger

from tg_bot.keyboards.copytrade import copytrade_keyboard_menu
from tg_bot.services.copytrade import CopyTradeService
from tg_bot.templates import render_copytrade_menu

router = Router()


async def copytrade(message: Message):
    """Handle copytrade menu button click"""
    s = CopyTradeService()
    if message.from_user is None:
        logger.warning("No message found in update")
        return
    records = await s.list_by_owner(message.from_user.id)
    total = len(records)
    active_cnt = 0
    for record in records:
        if record.active:
            active_cnt += 1

    text = render_copytrade_menu(
        total=total,
        active_cnt=active_cnt,
    )
    keyboard = copytrade_keyboard_menu(records)
    await message.answer(text, reply_markup=keyboard)
