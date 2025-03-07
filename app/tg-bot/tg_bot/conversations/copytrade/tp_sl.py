"""take profit and stop loss conversation"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from tg_bot.conversations.states import CopyTradeStates

router = Router()


@router.callback_query(F.data == "toggle_take_profile_and_stop_loss", CopyTradeStates.CREATING)
@router.callback_query(F.data == "toggle_take_profile_and_stop_loss", CopyTradeStates.EDITING)
async def toggle_take_profile_and_stop_loss(callback: CallbackQuery, state: FSMContext):
    """Toggle take profit and stop loss settings"""
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    await callback.answer("此功能正在开发中")
