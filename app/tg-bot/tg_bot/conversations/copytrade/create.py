import asyncio
from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply, Message
from loguru import logger
from solbot_common.types.copytrade import CopyTrade
from solbot_services.bot_setting import BotSettingService as SettingService

from tg_bot.conversations.copytrade.render import render
from tg_bot.conversations.states import CopyTradeStates
from tg_bot.keyboards.copytrade import create_copytrade_keyboard
from tg_bot.services.copytrade import CopyTradeService
from tg_bot.services.user import UserService
from tg_bot.templates import CREATE_COPYTRADE_MESSAGE
from tg_bot.utils import validate_solana_address

router = Router()
copy_trade_service = CopyTradeService()
setting_service = SettingService()
user_service = UserService()


@router.callback_query(F.data == "create_copytrade")
async def start_create_copytrade(callback: CallbackQuery, state: FSMContext):
    """Handle create copytrade button click"""
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    chat_id = callback.message.chat.id
    pubkey = await user_service.get_pubkey(chat_id=chat_id)

    # Initialize copytrade settings
    copytrade_settings = CopyTrade(
        owner=pubkey,
        chat_id=chat_id,
    )

    # Store settings in state
    await state.update_data(copytrade_settings=copytrade_settings)

    keyboard = create_copytrade_keyboard(copytrade_settings)

    await callback.message.edit_text(
        CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    await state.set_state(CopyTradeStates.CREATING)


@router.callback_query(F.data == "set_address", CopyTradeStates.CREATING)
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
        "👋 请输入要跟单的目标钱包地址：",
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )

    await state.set_state(CopyTradeStates.CREATE_WAITING_FOR_ADDRESS)


@router.message(CopyTradeStates.CREATE_WAITING_FOR_ADDRESS)
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
    copytrade_settings: CopyTrade = data["copytrade_settings"]

    # Update settings
    copytrade_settings.target_wallet = address
    await state.update_data(copytrade_settings=copytrade_settings)

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
    keyboard = create_copytrade_keyboard(copytrade_settings)

    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        text=CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    await state.set_state(CopyTradeStates.CREATING)


@router.callback_query(F.data == "set_wallet_alias", CopyTradeStates.CREATING)
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

    await state.set_state(CopyTradeStates.CREATE_WAITING_FOR_ALIAS)


@router.message(CopyTradeStates.CREATE_WAITING_FOR_ALIAS)
async def handle_set_alias(message: Message, state: FSMContext):
    if not message.text:
        return

    alias = message.text.strip()

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    # Update settings
    copytrade_settings.wallet_alias = alias
    await state.update_data(copytrade_settings=copytrade_settings)

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
        text=CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_copytrade_keyboard(copytrade_settings),
    )

    await state.set_state(CopyTradeStates.CREATING)


@router.callback_query(F.data == "set_fixed_buy_amount", CopyTradeStates.CREATING)
async def start_set_fixed_buy_amount(callback: CallbackQuery, state: FSMContext):
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
        "👋 请输入固定买入数量：",
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )

    await state.set_state(CopyTradeStates.CREATE_WAITING_FOR_FIXED_BUY_AMOUNT)


@router.message(CopyTradeStates.CREATE_WAITING_FOR_FIXED_BUY_AMOUNT)
async def handle_set_fixed_buy_amount(message: Message, state: FSMContext):
    if not message.text:
        return

    fixed_buy_amount = message.text.strip()

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    try:
        fixed_buy_amount = float(fixed_buy_amount)
    except ValueError:
        msg = await message.reply("❌ 无效的买入数量，请重新输入：", reply_markup=ForceReply())
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    if fixed_buy_amount <= 0 or fixed_buy_amount < 0.00000001:
        msg = await message.reply("❌ 无效的买入数量，请重新输入：", reply_markup=ForceReply())
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    # Update settings
    copytrade_settings.fixed_buy_amount = fixed_buy_amount
    await state.update_data(copytrade_settings=copytrade_settings)

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
        text=CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_copytrade_keyboard(copytrade_settings),
    )

    await state.set_state(CopyTradeStates.CREATING)


@router.callback_query(F.data == "toggle_auto_follow", CopyTradeStates.CREATING)
async def toggle_auto_follow(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    if copytrade_settings.auto_follow is True:
        return

    copytrade_settings.auto_follow = True
    copytrade_settings.stop_loss = False
    copytrade_settings.no_sell = False
    await state.update_data(copytrade_settings=copytrade_settings)

    await callback.message.edit_text(
        CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_copytrade_keyboard(copytrade_settings),
    )


# @router.callback_query(F.data == "toggle_stop_loss", CopyTradeStates.CREATING)
# async def toggle_stop_loss(callback: CallbackQuery, state: FSMContext):
#     if callback.message is None:
#         logger.warning("No message found in update")
#         return
#
#     if not isinstance(callback.message, Message):
#         logger.warning("Message is not a Message object")
#         return
#
#     # Get stored data
#     data = await state.get_data()
#     copytrade_settings: CopyTrade | None = cast(
#         CopyTrade | None, data.get("copytrade_settings")
#     )
#
#     if copytrade_settings is None:
#         logger.warning("Copytrade settings not found in state")
#         return
#
#     if copytrade_settings.stop_loss is True:
#         return
#
#     copytrade_settings.stop_loss = True
#     copytrade_settings.auto_follow = False
#     copytrade_settings.no_sell = False
#     await state.update_data(copytrade_settings=copytrade_settings)
#
#     await callback.message.edit_text(
#         CREATE_COPYTRADE_MESSAGE,
#         parse_mode="HTML",
#         reply_markup=create_copytrade_keyboard(copytrade_settings),
#     )


@router.callback_query(F.data == "toggle_no_sell", CopyTradeStates.CREATING)
async def toggle_no_sell(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    if copytrade_settings.no_sell is True:
        return

    copytrade_settings.no_sell = True
    copytrade_settings.auto_follow = False
    copytrade_settings.stop_loss = False
    await state.update_data(copytrade_settings=copytrade_settings)

    await callback.message.edit_text(
        CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_copytrade_keyboard(copytrade_settings),
    )


@router.callback_query(F.data == "set_priority", CopyTradeStates.CREATING)
async def start_set_priority(callback: CallbackQuery, state: FSMContext):
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
        "👋 请输入优先费用:",
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )

    await state.set_state(CopyTradeStates.CREATE_WAITING_FOR_PRIORITY)


@router.message(CopyTradeStates.CREATE_WAITING_FOR_PRIORITY)
async def handle_set_priority(message: Message, state: FSMContext):
    if not message.text:
        return

    priority = message.text.strip()

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    try:
        priority = float(priority)
    except ValueError:
        msg = await message.answer("❌ 无效的优先费用，请重新输入：", reply_markup=ForceReply())
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    if priority <= 0:
        msg = await message.answer("❌ 无效的优先费用，请重新输入：", reply_markup=ForceReply())
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    # Update settings
    copytrade_settings.priority = priority
    await state.update_data(copytrade_settings=copytrade_settings)

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
        text=CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_copytrade_keyboard(copytrade_settings),
    )

    await state.set_state(CopyTradeStates.CREATING)


@router.callback_query(F.data == "toggle_anti_sandwich", CopyTradeStates.CREATING)
async def toggle_anti_sandwich(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    copytrade_settings.anti_sandwich = not copytrade_settings.anti_sandwich
    await state.update_data(copytrade_settings=copytrade_settings)

    await callback.message.edit_text(
        CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_copytrade_keyboard(copytrade_settings),
    )


@router.callback_query(F.data == "toggle_auto_slippage", CopyTradeStates.CREATING)
async def toggle_auto_slippage(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    copytrade_settings.auto_slippage = not copytrade_settings.auto_slippage
    await state.update_data(copytrade_settings=copytrade_settings)

    await callback.message.edit_text(
        CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_copytrade_keyboard(copytrade_settings),
    )


@router.callback_query(F.data == "set_custom_slippage", CopyTradeStates.CREATING)
async def start_set_custom_slippage(callback: CallbackQuery, state: FSMContext):
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
        "👋 请输入自定义滑点:",
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )

    await state.set_state(CopyTradeStates.CREATE_WAITING_FOR_CUSTOM_SLIPPAGE)


@router.message(CopyTradeStates.CREATE_WAITING_FOR_CUSTOM_SLIPPAGE)
async def handle_set_custom_slippage(message: Message, state: FSMContext):
    if not message.text:
        return

    custom_slippage = message.text.strip()

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    try:
        custom_slippage = float(custom_slippage)
    except ValueError:
        msg = await message.reply("❌ 无效的自定义滑点，请重新输入：", reply_markup=ForceReply())
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    if custom_slippage <= 0 or custom_slippage > 100:
        msg = await message.reply("❌ 无效的自定义滑点，请重新输入：", reply_markup=ForceReply())
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    # Update settings
    copytrade_settings.custom_slippage = custom_slippage
    copytrade_settings.auto_slippage = False
    await state.update_data(copytrade_settings=copytrade_settings)

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
        text=CREATE_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_copytrade_keyboard(copytrade_settings),
    )

    await state.set_state(CopyTradeStates.CREATING)


@router.callback_query(F.data == "back_to_copytrade", CopyTradeStates.CREATING)
async def cancel_copytrade(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(CopyTradeStates.MENU)


@router.callback_query(F.data == "submit_copytrade", CopyTradeStates.CREATING)
async def submit_copytrade(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(CopyTrade | None, data.get("copytrade_settings"))

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    # Validate copytrade settings
    if copytrade_settings.target_wallet is None:
        # 发送错误消息并在 10 秒后删除
        error_message = await callback.message.answer("❌ 创建失败，请设置正确的跟单地址")

        # 创建一个异步任务来删除消息
        async def delete_message_later(message: Message, delay: int):
            await asyncio.sleep(delay)
            try:
                await message.delete()
            except Exception as e:
                logger.warning(f"Failed to delete message: {e}")

        delete_task = asyncio.create_task(delete_message_later(error_message, 10))
        # 添加任务完成回调以处理可能的异常
        delete_task.add_done_callback(lambda t: t.exception() if t.exception() else None)
        return

    # 写入数据库
    try:
        await copy_trade_service.add(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to add copytrade: {e}")
        # 发送错误消息并在 10 秒后删除
        error_message = await callback.message.answer("❌ 创建失败，请稍后重试")

        # 创建一个异步任务来删除消息
        async def delete_message_later(message: Message, delay: int):
            await asyncio.sleep(delay)
            try:
                await message.delete()
            except Exception as e:
                logger.warning(f"Failed to delete message: {e}")

        delete_task = asyncio.create_task(delete_message_later(error_message, 10))
        # 添加任务完成回调以处理可能的异常
        delete_task.add_done_callback(lambda t: t.exception() if t.exception() else None)
        return

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(CopyTradeStates.MENU)
    logger.info(f"Copytrade created successfully, id: {copytrade_settings}")
