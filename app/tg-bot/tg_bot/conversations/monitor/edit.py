import re
from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply, Message
from solbot_common.log import logger

from tg_bot.conversations.monitor.render import render
from tg_bot.conversations.states import MonitorStates
from tg_bot.keyboards.common import back_keyboard, confirm_keyboard
from tg_bot.keyboards.monitor import edit_monitor_keyboard
from tg_bot.models.monitor import Monitor
from tg_bot.services.monitor import MonitorService
from tg_bot.templates import render_edit_monitor_message

router = Router()
monitor_service = MonitorService()

# Regular expression to match monitor_{id} pattern
MONITOR_PATTERN = re.compile(r"monitor_(\d+)")


@router.callback_query(lambda c: MONITOR_PATTERN.match(c.data))
async def handle_monitor_selection(callback: CallbackQuery, state: FSMContext):
    """Handle selection of a specific monitor item"""
    if callback.message is None:
        return

    if not isinstance(callback.message, Message):
        return

    if callback.data is None:
        logger.warning("No data found in callback")
        return

    # Extract the monitor ID from callback data
    match = MONITOR_PATTERN.match(callback.data)
    if not match:
        logger.warning("Invalid callback data for monitor selection")
        return

    monitor_id = int(match.group(1))

    # Fetch the monitor data
    monitor = await monitor_service.get_by_id(monitor_id)
    if monitor is None:
        await callback.answer("❌ 监听不存在或已被删除")
        return

    # Store monitor ID in state
    await state.update_data(monitor_id=monitor_id)
    await state.update_data(monitor=monitor)

    # Show edit keyboard for the selected monitor
    keyboard = edit_monitor_keyboard(monitor)
    await callback.message.edit_text(
        text=render_edit_monitor_message(monitor), reply_markup=keyboard
    )
    await state.set_state(MonitorStates.EDITING)


@router.callback_query(F.data == "set_wallet_alias", MonitorStates.EDITING)
async def start_set_alias(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Store original message details for later updates
    await state.update_data(
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
    )

    # Send prompt message with force reply
    msg = await callback.message.answer(
        "👋 请输入钱包别名：",
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )

    await state.set_state(MonitorStates.EDIT_WAITING_FOR_ALIAS)


@router.message(MonitorStates.EDIT_WAITING_FOR_ALIAS)
async def handle_set_alias(message: Message, state: FSMContext):
    if not message.text:
        return

    alias = message.text.strip()

    # Get stored data
    data = await state.get_data()
    monitor: Monitor | None = cast(Monitor | None, data.get("monitor"))

    if monitor is None:
        logger.warning("Monitor not found in state")
        return

    # Update settings
    monitor.wallet_alias = alias
    await state.update_data(monitor=monitor)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    try:
        await message.delete()  # Delete user's input
        await message.bot.delete_message(  # Delete prompt message
            chat_id=data["prompt_chat_id"],
            message_id=data["prompt_message_id"],
        )
    except Exception as e:
        logger.warning(f"Failed to delete messages: {e}")

    # Save changes to the database
    try:
        await monitor_service.update(monitor)
    except Exception as e:
        logger.warning(f"Failed to update monitor: {e}")
        return

    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        text=render_edit_monitor_message(monitor),
        parse_mode="HTML",
        reply_markup=edit_monitor_keyboard(monitor),
    )

    await state.set_state(MonitorStates.EDITING)


@router.callback_query(F.data == "delete_monitor", MonitorStates.EDITING)
async def delete_monitor(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # 记录当前消息，如果后续确认删除的话，当前这条消息也需要被删除
    await state.update_data(
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
    )

    text = "⚠️ 您正在删除一个交易监听, 请您确认:"
    await callback.message.reply(
        text,
        parse_mode="HTML",
        reply_markup=confirm_keyboard("confirm_delete_monitor", "cancel_delete_monitor"),
    )


@router.callback_query(F.data == "confirm_delete_monitor", MonitorStates.EDITING)
async def confirm_delete_monitor(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    monitor: Monitor | None = cast(Monitor | None, data.get("monitor"))

    if monitor is None:
        logger.warning("Monitor not found in state")
        return

    await monitor_service.delete(monitor)

    # 删除 原始消息
    original_message_id = data.get("original_message_id")
    original_chat_id = data.get("original_chat_id")
    if (
        original_message_id is not None
        and original_chat_id is not None
        and callback.message.bot is not None
    ):
        await callback.message.bot.delete_message(
            chat_id=original_chat_id, message_id=original_message_id
        )

    # 发送删除成功的消息
    await callback.message.edit_text(
        "✅ 您已成功删除一个交易监听",
        parse_mode="HTML",
        reply_markup=back_keyboard("back_to_monitor"),
    )
    # clear monitor data
    await state.update_data(monitor=None)


@router.callback_query(F.data == "cancel_delete_monitor", MonitorStates.EDITING)
async def cancel_delete_monitor(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # 删除 确认消息
    await callback.message.delete()


@router.callback_query(F.data == "toggle_monitor", MonitorStates.EDITING)
async def toggle_monitor(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    monitor: Monitor | None = cast(Monitor | None, data.get("monitor"))

    if monitor is None:
        logger.warning("Monitor not found in state")
        return

    monitor.active = not monitor.active
    await state.update_data(monitor=monitor)

    try:
        await monitor_service.update(monitor)
    except Exception as e:
        logger.warning(f"Failed to update monitor: {e}")
        return

    await callback.message.edit_text(
        render_edit_monitor_message(monitor),
        parse_mode="HTML",
        reply_markup=edit_monitor_keyboard(monitor),
    )


@router.callback_query(F.data == "back_to_monitor", MonitorStates.EDITING)
async def back_to_monitor(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # clear monitor data
    await state.update_data(monitor=None)

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(MonitorStates.MENU)
