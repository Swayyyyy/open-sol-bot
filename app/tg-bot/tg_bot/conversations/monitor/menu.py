from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from tg_bot.conversations.states import MonitorStates
from tg_bot.services.monitor import MonitorService
from tg_bot.utils import delete_later
from .render import render

router = Router()


@router.callback_query(F.data == "monitor")
async def enter_monitor_menu(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(MonitorStates.MENU)


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


@router.callback_query(F.data == "stop_all_monitor")
async def stop_all_monitor(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    try:
        await MonitorService().inactive_all(callback.from_user.id)
    except Exception as e:
        logger.exception(e)
        msg = await callback.message.answer("停止全部监听失败, 请稍后重试")
        await delete_later(msg)

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(MonitorStates.MENU)
