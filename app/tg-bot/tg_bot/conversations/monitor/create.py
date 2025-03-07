from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply, Message
from loguru import logger

from tg_bot.conversations.states import MonitorStates
from tg_bot.keyboards.monitor import create_monitor_keyboard
from tg_bot.models.monitor import Monitor
from tg_bot.services.monitor import MonitorService
from tg_bot.templates import CREATE_MONITOR_MESSAGE
from tg_bot.utils import delete_later, validate_solana_address

from .render import render


router = Router()
monitor_service = MonitorService()


@router.callback_query(F.data == "create_new_monitor")
async def create_new_monitor(callback: CallbackQuery, state: FSMContext):
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

    # Store default monitor settings
    monitor = Monitor(
        chat_id=callback.message.chat.id,
        active=True,
    )
    await state.update_data(
        monitor_settings=monitor,
    )

    await callback.message.edit_text(
        CREATE_MONITOR_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_monitor_keyboard(monitor),
    )

    await state.set_state(MonitorStates.CREATING)


@router.callback_query(F.data == "set_address", MonitorStates.CREATING)
async def start_set_address(callback: CallbackQuery, state: FSMContext):
    """Handle set address button click"""
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
        "👋 请输入要监听的钱包地址：",
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )

    await state.set_state(MonitorStates.CREATE_WAITING_FOR_ADDRESS)


@router.message(MonitorStates.CREATE_WAITING_FOR_ADDRESS)
async def handle_set_address(message: Message, state: FSMContext):
    """Handle wallet address input"""
    if not message.text:
        return

    address = message.text.strip()

    # Validate address
    if not validate_solana_address(address):
        msg = await message.answer(
            "❌ 无效的 Solana 钱包地址，请重新输入：", reply_markup=ForceReply()
        )
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=msg.chat.id,
                message_id=msg.message_id,
            )
        return

    # Get stored data
    data = await state.get_data()
    monitor_settings: Monitor = data["monitor_settings"]

    # Update settings
    monitor_settings.target_wallet = address
    await state.update_data(monitor_settings=monitor_settings)

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

    # Update original message
    keyboard = create_monitor_keyboard(monitor_settings)

    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        text=CREATE_MONITOR_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    await state.set_state(MonitorStates.CREATING)


@router.callback_query(F.data == "set_wallet_alias", MonitorStates.CREATING)
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

    await state.set_state(MonitorStates.CREATE_WAITING_FOR_ALIAS)


@router.message(MonitorStates.CREATE_WAITING_FOR_ALIAS)
async def handle_set_alias(message: Message, state: FSMContext):
    if not message.text:
        return

    alias = message.text.strip()

    # Get stored data
    data = await state.get_data()
    monitor_settings: Monitor | None = cast(Monitor | None, data.get("monitor_settings"))

    if monitor_settings is None:
        logger.warning("Monitor settings not found in state")
        return

    # Update settings
    monitor_settings.wallet_alias = alias
    await state.update_data(monitor_settings=monitor_settings)

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

    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        text=CREATE_MONITOR_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_monitor_keyboard(monitor_settings),
    )

    await state.set_state(MonitorStates.CREATING)


@router.callback_query(F.data == "back_to_monitor", MonitorStates.CREATING)
async def back_parent(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(MonitorStates.MENU)


@router.callback_query(F.data == "submit_monitor", MonitorStates.CREATING)
async def submit_monitor(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    data = await state.get_data()
    monitor_settings: Monitor | None = cast(Monitor | None, data.get("monitor_settings"))

    if monitor_settings is None:
        logger.warning("Monitor settings not found in state")
        return

    if monitor_settings.target_wallet is None:
        # 发送错误消息并在 10 秒后删除
        error_message = await callback.message.answer("❌ 创建失败，请设置正确的跟单地址")
        await delete_later(error_message)
        return

    # 写入数据库
    try:
        await monitor_service.add(monitor_settings)
    except Exception as e:
        logger.warning(f"Failed to add monitor: {e}")
        error_message = await callback.message.answer("❌ 创建失败，请稍后重试")
        await delete_later(error_message)
        return

    data = await render(callback)
    await state.set_state(MonitorStates.MENU)
    await callback.message.edit_text(**data)
    logger.info(f"Monitor created successfully, id: {monitor_settings}")
