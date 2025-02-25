from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from tg_bot.conversations.copytrade.render import render
from tg_bot.conversations.states import CopyTradeStates
from tg_bot.services.copytrade import CopyTradeService
from tg_bot.utils import delete_later

router = Router()


@router.callback_query(F.data == "copytrade")
async def start_copytrade(callback: CallbackQuery, state: FSMContext):
    """Handle copytrade menu button click"""
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(CopyTradeStates.MENU)


@router.callback_query(F.data == "stop_all_copytrade")
async def stop_all_copytrade(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    try:
        await CopyTradeService().inactive_all(callback.from_user.id)
    except Exception as e:
        logger.exception(e)
        msg = await callback.message.answer("停止全部跟单失败, 请稍后重试")
        await delete_later(msg)

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(CopyTradeStates.MENU)


@router.callback_query(F.data == "refresh_copytrade")
async def refresh_copytrade(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(CopyTradeStates.MENU)


@router.callback_query(F.data == "back_to_home")
async def back_to_home(callback: CallbackQuery):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    from tg_bot.conversations.home.render import render

    data = await render(callback)
    await callback.message.edit_text(**data)
