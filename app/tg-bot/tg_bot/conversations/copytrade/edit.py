import re
from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply, Message

from common.log import logger
from tg_bot.conversations.copytrade.render import render
from tg_bot.conversations.states import CopyTradeStates
from tg_bot.keyboards.common import back_keyboard, confirm_keyboard
from tg_bot.keyboards.copytrade import edit_copytrade_keyboard
from common.types.copytrade import CopyTrade
from tg_bot.services.copytrade import CopyTradeService
from tg_bot.templates import EDIT_COPYTRADE_MESSAGE
from tg_bot.utils import cleanup_conversation_messages

router = Router()
copy_trade_service = CopyTradeService()

# Regular expression to match copytrade_{id} pattern
COPYTRADE_PATTERN = re.compile(r"copytrade_(\d+)")


@router.callback_query(lambda c: COPYTRADE_PATTERN.match(c.data))
async def handle_copytrade_selection(callback: CallbackQuery, state: FSMContext):
    """Handle selection of a specific copytrade item"""
    if callback.message is None:
        return

    if not isinstance(callback.message, Message):
        return

    if callback.data is None:
        logger.warning("No data found in callback")
        return

    # Extract the copytrade ID from callback data
    match = COPYTRADE_PATTERN.match(callback.data)
    if not match:
        logger.warning("Invalid callback data for copytrade selection")
        return

    copytrade_id = int(match.group(1))

    # Fetch the copytrade data
    copytrade = await copy_trade_service.get_by_id(copytrade_id)
    copytrade_settings = copytrade
    if copytrade is None:
        await callback.answer("❌ 跟单不存在或已被删除")
        return

    # Store copytrade ID in state
    await state.update_data(copytrade_id=copytrade_id)
    await state.update_data(copytrade_settings=copytrade_settings)

    # Show edit keyboard for the selected copytrade
    keyboard = edit_copytrade_keyboard(copytrade)
    await callback.message.edit_text(text=EDIT_COPYTRADE_MESSAGE, reply_markup=keyboard)
    await state.set_state(CopyTradeStates.EDITING)


@router.callback_query(F.data == "set_wallet_alias", CopyTradeStates.EDITING)
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

    await state.set_state(CopyTradeStates.EDIT_WAITING_FOR_ALIAS)


@router.message(CopyTradeStates.EDIT_WAITING_FOR_ALIAS)
async def handle_set_alias(message: Message, state: FSMContext):
    if not message.text:
        return

    alias = message.text.strip()

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    # Check if alias has changed
    if copytrade_settings.wallet_alias == alias:
        await state.set_state(CopyTradeStates.EDITING)
        await cleanup_conversation_messages(message, state)
        return

    # Update settings
    copytrade_settings.wallet_alias = alias
    await state.update_data(copytrade_settings=copytrade_settings)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    await cleanup_conversation_messages(message, state)

    # Save changes to the database
    await copy_trade_service.update(copytrade_settings)

    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        text=EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )

    await state.set_state(CopyTradeStates.EDITING)


@router.callback_query(F.data == "set_fixed_buy_amount", CopyTradeStates.EDITING)
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

    await state.set_state(CopyTradeStates.EDIT_WAITING_FOR_FIXED_BUY_AMOUNT)


@router.message(CopyTradeStates.EDIT_WAITING_FOR_FIXED_BUY_AMOUNT)
async def handle_set_fixed_buy_amount(message: Message, state: FSMContext):
    if not message.text:
        return

    fixed_buy_amount = message.text.strip()

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    try:
        fixed_buy_amount = float(fixed_buy_amount)
    except ValueError:
        msg = await message.reply(
            "❌ 无效的买入数量，请重新输入：", reply_markup=ForceReply()
        )
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
        msg = await message.reply(
            "❌ 无效的买入数量，请重新输入：", reply_markup=ForceReply()
        )
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    # Check if fixed_buy_amount has changed
    if copytrade_settings.fixed_buy_amount == fixed_buy_amount:
        await state.set_state(CopyTradeStates.EDITING)
        await cleanup_conversation_messages(message, state)
        return

    # Update settings
    copytrade_settings.fixed_buy_amount = fixed_buy_amount
    await state.update_data(copytrade_settings=copytrade_settings)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    try:
        await copy_trade_service.update(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to update copytrade: {e}")
        return

    # Clean up messages
    await cleanup_conversation_messages(message, state)
    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        text=EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )

    await state.set_state(CopyTradeStates.EDITING)


@router.callback_query(F.data == "toggle_auto_follow", CopyTradeStates.EDITING)
async def toggle_auto_follow(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    if copytrade_settings.auto_follow is True:
        return

    copytrade_settings.auto_follow = True
    copytrade_settings.stop_loss = False
    copytrade_settings.no_sell = False
    await state.update_data(copytrade_settings=copytrade_settings)
    try:
        await copy_trade_service.update(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to update copytrade: {e}")
        return

    await callback.message.edit_text(
        EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )


# @router.callback_query(F.data == "toggle_stop_loss", CopyTradeStates.EDITING)
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
#     try:
#         await copy_trade_service.update(copytrade_settings)
#     except Exception as e:
#         logger.warning(f"Failed to update copytrade: {e}")
#         return
#
#     await callback.message.edit_text(
#         EDIT_COPYTRADE_MESSAGE,
#         parse_mode="HTML",
#         reply_markup=edit_copytrade_keyboard(copytrade_settings),
#     )


@router.callback_query(F.data == "toggle_no_sell", CopyTradeStates.EDITING)
async def toggle_no_sell(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    if copytrade_settings.no_sell is True:
        return

    copytrade_settings.no_sell = True
    copytrade_settings.auto_follow = False
    copytrade_settings.stop_loss = False
    await state.update_data(copytrade_settings=copytrade_settings)
    try:
        await copy_trade_service.update(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to update copytrade: {e}")
        return

    await callback.message.edit_text(
        EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )


@router.callback_query(F.data == "set_priority", CopyTradeStates.EDITING)
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

    await state.set_state(CopyTradeStates.EDIT_WAITING_FOR_PRIORITY)


@router.message(CopyTradeStates.EDIT_WAITING_FOR_PRIORITY)
async def handle_set_priority(message: Message, state: FSMContext):
    if not message.text:
        return

    priority = message.text.strip()

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    try:
        priority = float(priority)
    except ValueError:
        msg = await message.reply(
            "❌ 无效的优先费用，请重新输入：", reply_markup=ForceReply()
        )
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
        msg = await message.reply(
            "❌ 无效的优先费用，请重新输入：", reply_markup=ForceReply()
        )
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    # Check if priority has changed
    if copytrade_settings.priority == priority:
        await state.set_state(CopyTradeStates.EDITING)
        await cleanup_conversation_messages(message, state)
        return

    # Update settings
    copytrade_settings.priority = priority
    await state.update_data(copytrade_settings=copytrade_settings)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    await cleanup_conversation_messages(message, state)

    try:
        await copy_trade_service.update(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to update copytrade: {e}")
        return

    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        text=EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )

    await state.set_state(CopyTradeStates.EDITING)


@router.callback_query(F.data == "toggle_anti_sandwich", CopyTradeStates.EDITING)
async def toggle_anti_sandwich(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    copytrade_settings.anti_sandwich = not copytrade_settings.anti_sandwich
    await state.update_data(copytrade_settings=copytrade_settings)

    try:
        await copy_trade_service.update(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to update copytrade: {e}")
        return

    await callback.message.edit_text(
        EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )


@router.callback_query(F.data == "toggle_auto_slippage", CopyTradeStates.EDITING)
async def toggle_auto_slippage(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    copytrade_settings.auto_slippage = not copytrade_settings.auto_slippage
    await state.update_data(copytrade_settings=copytrade_settings)

    try:
        await copy_trade_service.update(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to update copytrade: {e}")
        return

    await callback.message.edit_text(
        EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )


@router.callback_query(F.data == "set_custom_slippage", CopyTradeStates.EDITING)
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

    await state.set_state(CopyTradeStates.EDIT_WAITING_FOR_CUSTOM_SLIPPAGE)


@router.message(CopyTradeStates.EDIT_WAITING_FOR_CUSTOM_SLIPPAGE)
async def handle_set_custom_slippage(message: Message, state: FSMContext):
    if not message.text:
        return

    custom_slippage = message.text.strip()

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    try:
        custom_slippage = float(custom_slippage)
    except ValueError:
        msg = await message.reply(
            "❌ 无效的自定义滑点，请重新输入：", reply_markup=ForceReply()
        )
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
        msg = await message.reply(
            "❌ 无效的自定义滑点，请重新输入：", reply_markup=ForceReply()
        )
        await state.update_data(prompt_message_id=msg.message_id)
        await state.update_data(prompt_chat_id=msg.chat.id)
        if message.bot is not None:
            await message.delete()
            await message.bot.delete_message(  # Delete prompt message
                chat_id=data["prompt_chat_id"],
                message_id=data["prompt_message_id"],
            )
        return

    if copytrade_settings.custom_slippage == custom_slippage:
        await state.set_state(CopyTradeStates.EDITING)
        await cleanup_conversation_messages(message, state)
        return

    # Update settings
    copytrade_settings.custom_slippage = custom_slippage
    copytrade_settings.auto_slippage = False
    await state.update_data(copytrade_settings=copytrade_settings)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    await cleanup_conversation_messages(message, state)

    try:
        await copy_trade_service.update(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to update copytrade: {e}")
        return

    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        text=EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )

    await state.set_state(CopyTradeStates.EDITING)


@router.callback_query(F.data == "delete_copytrade", CopyTradeStates.EDITING)
async def delete_copytrade(callback: CallbackQuery, state: FSMContext):
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

    text = "⚠️ 您正在删除一个跟单交易, 请您确认:"
    await callback.message.reply(
        text,
        parse_mode="HTML",
        reply_markup=confirm_keyboard(
            "confirm_delete_copytrade", "cancel_delete_copytrade"
        ),
    )


@router.callback_query(F.data == "confirm_delete_copytrade", CopyTradeStates.EDITING)
async def confirm_delete_copytrade(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    await copy_trade_service.delete(copytrade_settings)

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
        "✅ 您已成功删除一个跟单交易",
        parse_mode="HTML",
        reply_markup=back_keyboard("back_to_copytrade"),
    )
    # clear copytrade data
    await state.update_data(copytrade_id=None)
    await state.update_data(copytrade_settings=None)


@router.callback_query(F.data == "cancel_delete_copytrade", CopyTradeStates.EDITING)
async def cancel_delete_copytrade(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # 删除 确认消息
    await callback.message.delete()


@router.callback_query(F.data == "toggle_copytrade", CopyTradeStates.EDITING)
async def toggle_copytrade(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # Get stored data
    data = await state.get_data()
    copytrade_settings: CopyTrade | None = cast(
        CopyTrade | None, data.get("copytrade_settings")
    )

    if copytrade_settings is None:
        logger.warning("Copytrade settings not found in state")
        return

    copytrade_settings.active = not copytrade_settings.active
    await state.update_data(copytrade_settings=copytrade_settings)

    try:
        await copy_trade_service.update(copytrade_settings)
    except Exception as e:
        logger.warning(f"Failed to update copytrade: {e}")
        return

    await callback.message.edit_text(
        EDIT_COPYTRADE_MESSAGE,
        parse_mode="HTML",
        reply_markup=edit_copytrade_keyboard(copytrade_settings),
    )


@router.callback_query(F.data == "back_to_copytrade", CopyTradeStates.EDITING)
async def back_to_copytrade(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    # clear copytrade data
    await state.update_data(copytrade_id=None)
    await state.update_data(copytrade_settings=None)

    data = await render(callback)
    await callback.message.edit_text(**data)
    await state.set_state(CopyTradeStates.MENU)
