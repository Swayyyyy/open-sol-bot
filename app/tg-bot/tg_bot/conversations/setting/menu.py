import re
from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply, Message
from loguru import logger

from tg_bot.conversations.setting.render import render
from tg_bot.conversations.states import SettingStates
from common.types.bot_setting import BotSetting as Setting
from services.bot_setting import BotSettingService as SettingService
from tg_bot.services.user import UserService
from tg_bot.utils import (
    cleanup_conversation_messages,
    get_setting_from_db,
    invalid_input_and_request_reinput,
)
from .template import SET_QUICK_SLIPPAGE_PROMPT, SET_SANDWICH_SLIPPAGE_PROMPT

router = Router()

setting_service = SettingService()
user_service = UserService()


async def setting_menu(
    callback: CallbackQuery, state: FSMContext, replace: bool = True
):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    setting = await get_setting_from_db(callback.from_user.id)
    if setting is None:
        setting = await get_setting_from_db(callback.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    await state.update_data(
        setting=setting,
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
    )
    data = await render(callback, setting)
    if replace:
        await callback.message.edit_text(**data)
    else:
        await callback.message.answer(**data)


@router.callback_query(F.data == "set")
async def _setting_menu(callback: CallbackQuery, state: FSMContext):
    await setting_menu(callback, state)


@router.callback_query(F.data == "back_to_home")
async def back_to_home(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    from tg_bot.conversations.home.render import render

    data = await render(callback)
    await state.clear()
    await callback.message.edit_text(**data)


@router.callback_query(F.data == "setting:toggle_auto_slippage")
async def toggle_auto_slippage(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        setting = await get_setting_from_db(callback.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    setting.auto_slippage = not setting.auto_slippage
    if setting.auto_slippage:
        setting.sandwich_mode = False
    await state.update_data(setting=setting)
    await setting_service.set(setting)

    data = await render(callback)
    await callback.message.edit_text(**data)


@router.callback_query(F.data == "setting:edit_quick_slippage")
async def edit_quick_slippage(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    await state.update_data(
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
    )

    # Send prompt message with force reply
    msg = await callback.message.answer(
        SET_QUICK_SLIPPAGE_PROMPT,
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )

    await state.set_state(SettingStates.WAITING_FOR_QUICK_SLIPPAGE)


@router.message(SettingStates.WAITING_FOR_QUICK_SLIPPAGE, F.text)
async def handle_quick_slippage(message: Message, state: FSMContext):
    if not message.text:
        return

    try:
        slippage = int(message.text.strip())
    except ValueError:
        return await invalid_input_and_request_reinput(
            text="❌ 快速滑点必须是一个数字(0-100)，请重新输入：",
            last_message=message,
            state=state,
        )

    if slippage <= 0 or slippage > 100:
        return await invalid_input_and_request_reinput(
            text="❌ 快速滑点必须在 0 到 100 之间，请重新输入：",
            last_message=message,
            state=state,
        )

    data = await state.get_data()
    setting: Setting | None = data.get("setting")
    if setting is None:
        if message.from_user is None:
            raise ValueError("Setting not found")
        setting = await get_setting_from_db(message.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    if setting.get_quick_slippage_pct() == slippage:
        await cleanup_conversation_messages(message, state)
        return

    # Update settings
    setting.set_quick_slippage(slippage)
    await state.update_data(setting=setting)
    await setting_service.set(setting)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    await cleanup_conversation_messages(message, state)

    render_data = await render(message, setting)
    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        **render_data,
    )


@router.callback_query(F.data == "setting:edit_sandwich_slippage")
async def edit_sandwich_slippage(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    await state.update_data(
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
    )

    # Send prompt message with force reply
    msg = await callback.message.answer(
        SET_SANDWICH_SLIPPAGE_PROMPT,
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )

    await state.set_state(SettingStates.WAITING_FOR_SANDWICH_SLIPPAGE)


@router.message(SettingStates.WAITING_FOR_SANDWICH_SLIPPAGE)
async def handle_sandwich_slippage(message: Message, state: FSMContext):
    if not message.text:
        return

    try:
        sandwich_slippage = int(message.text.strip())
    except ValueError:
        return await invalid_input_and_request_reinput(
            text="❌ 防夹滑点必须是一个数字(0-100)，请重新输入：",
            last_message=message,
            state=state,
        )

    if sandwich_slippage <= 0 or sandwich_slippage > 100:
        return await invalid_input_and_request_reinput(
            text="❌ 防夹滑点必须在 0 到 100 之间，请重新输入：",
            last_message=message,
            state=state,
        )

    data = await state.get_data()
    setting: Setting | None = data.get("setting")
    if setting is None:
        if message.from_user is None:
            raise ValueError("Setting not found")
        setting = await get_setting_from_db(message.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    if setting.get_sandwich_slippage_pct() == sandwich_slippage:
        await cleanup_conversation_messages(message, state)
        return

    # Update settings
    setting.set_sandwich_slippage(sandwich_slippage)
    await state.update_data(setting=setting)
    await setting_service.set(setting)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    await cleanup_conversation_messages(message, state)

    render_data = await render(message, setting)
    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        **render_data,
    )


@router.callback_query(F.data == "setting:edit_buy_priority_fee")
async def edit_buy_priority_fee(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        setting = await get_setting_from_db(callback.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    await state.update_data(
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
    )

    # Send prompt message with force reply
    msg = await callback.message.answer(
        "👋 请输入买入优先费(当前 {}):".format(setting.buy_priority_fee),
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )
    await state.set_state(SettingStates.WAITING_FOR_BUY_PRIORITY_FEE)


@router.message(SettingStates.WAITING_FOR_BUY_PRIORITY_FEE)
async def handle_buy_priority_fee(message: Message, state: FSMContext):
    if not message.text:
        return

    try:
        buy_priority_fee = float(message.text.strip())
    except ValueError:
        return await invalid_input_and_request_reinput(
            text="❌ 买入优先费必须是一个数字，请重新输入：",
            last_message=message,
            state=state,
        )

    if buy_priority_fee < 0:
        return await invalid_input_and_request_reinput(
            text="❌ 买入优先费必须大于等于 0，请重新输入：",
            last_message=message,
            state=state,
        )

    data = await state.get_data()
    setting: Setting | None = data.get("setting")
    if setting is None:
        if message.from_user is None:
            raise ValueError("Setting not found")
        setting = await get_setting_from_db(message.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    if setting.buy_priority_fee == buy_priority_fee:
        await cleanup_conversation_messages(message, state)
        return

    # Update settings
    setting.buy_priority_fee = buy_priority_fee
    await state.update_data(setting=setting)
    await setting_service.set(setting)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    await cleanup_conversation_messages(message, state)

    render_data = await render(message, setting)
    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        **render_data,
    )

    # 重置 state 状态
    await state.set_state(None)


@router.callback_query(F.data == "setting:edit_sell_priority_fee")
async def edit_sell_priority_fee(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        setting = await get_setting_from_db(callback.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    await state.update_data(
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
    )

    # Send prompt message with force reply
    msg = await callback.message.answer(
        "👋 请输入卖出优先费(当前 {}):".format(setting.sell_priority_fee),
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )
    await state.set_state(SettingStates.WAITING_FOR_SELL_PRIORITY_FEE)


@router.message(SettingStates.WAITING_FOR_SELL_PRIORITY_FEE)
async def handle_sell_priority_fee(message: Message, state: FSMContext):
    if not message.text:
        return

    try:
        sell_priority_fee = float(message.text.strip())
    except ValueError:
        return await invalid_input_and_request_reinput(
            text="❌ 卖出优先费是数字，请重新输入：",
            last_message=message,
            state=state,
        )

    if sell_priority_fee < 0:
        return await invalid_input_and_request_reinput(
            text="❌ 卖出优先费必须大于等于 0，请重新输入：",
            last_message=message,
            state=state,
        )

    data = await state.get_data()
    setting: Setting | None = data.get("setting")
    if setting is None:
        if message.from_user is None:
            raise ValueError("Setting not found")
        setting = await get_setting_from_db(message.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    if setting.sell_priority_fee == sell_priority_fee:
        await cleanup_conversation_messages(message, state)
        return

    # Update settings
    setting.sell_priority_fee = sell_priority_fee
    await state.update_data(setting=setting)
    await setting_service.set(setting)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    await cleanup_conversation_messages(message, state)

    render_data = await render(message, setting)
    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        **render_data,
    )

    await state.set_state(None)


@router.callback_query(F.data == "setting:toggle_auto_buy")
async def toggle_auto_buy(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        setting = await get_setting_from_db(callback.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    setting.auto_buy = not setting.auto_buy
    await state.update_data(setting=setting)
    await setting_service.set(setting)

    data = await render(callback)
    await callback.message.edit_text(**data)


@router.callback_query(F.data == "setting:toggle_auto_sell")
async def toggle_auto_sell(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, Message):
        logger.warning("Message is not a Message object")
        return

    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        setting = await get_setting_from_db(callback.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    setting.auto_sell = not setting.auto_sell
    await state.update_data(setting=setting)
    await setting_service.set(setting)

    data = await render(callback)
    await callback.message.edit_text(**data)


BUY_AMOUNT_PATTERN = re.compile(r"setting:edit_buy_amount_(\d)")


@router.callback_query(lambda c: BUY_AMOUNT_PATTERN.match(c.data))
async def set_buy_amount(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        return

    if not isinstance(callback.message, Message):
        return

    if callback.data is None:
        logger.warning("No data found in callback")
        return

    # Extract the copytrade ID from callback data
    match = BUY_AMOUNT_PATTERN.match(callback.data)
    if not match:
        logger.warning("Invalid callback data for copytrade selection")
        return

    idx = int(match.group(1))
    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        setting = await get_setting_from_db(callback.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    if not hasattr(setting, f"custom_buy_amount_{idx}"):
        raise ValueError(f"Invalid buy amount index: {idx}")

    setting = cast(Setting, (await state.get_data()).get("setting"))
    current_amount = getattr(setting, f"custom_buy_amount_{idx}")

    # Send prompt message with force reply
    msg = await callback.message.answer(
        f"👋 请输入买入SOL数量(当前 {current_amount}):",
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
        buy_idx=idx,
    )
    await state.set_state(SettingStates.WAITING_FOR_CUSTOM_BUY_AMOUNT)


@router.message(SettingStates.WAITING_FOR_CUSTOM_BUY_AMOUNT)
async def handle_custom_buy_amount(message: Message, state: FSMContext):
    if not message.text:
        return

    try:
        buy_amount = float(message.text.strip())
    except ValueError:
        return await invalid_input_and_request_reinput(
            "❌ 数量必须大于等于 0，请重新输入：",
            message,
            state,
        )
        return

    if buy_amount <= 0:
        return await invalid_input_and_request_reinput(
            "❌ 数量必须大于等于 0，请重新输入：",
            message,
            state,
        )

    data = await state.get_data()
    if idx := data.get("buy_idx"):
        buy_idx = int(idx)
    else:
        raise ValueError("Buy index not found")

    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        if message.from_user is None:
            raise ValueError("Setting not found")
        setting = await get_setting_from_db(message.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    # Update settings
    if not hasattr(setting, f"custom_buy_amount_{buy_idx}"):
        raise ValueError(f"Invalid buy amount index: {buy_idx}")

    old_value = getattr(setting, f"custom_buy_amount_{buy_idx}")
    if old_value == buy_amount:
        await cleanup_conversation_messages(message, state)
        return

    setattr(setting, f"custom_buy_amount_{idx}", buy_amount)
    await setting_service.set(setting)
    await state.update_data(setting=setting)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    await cleanup_conversation_messages(message, state)

    render_data = await render(message, setting)
    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        **render_data,
    )

    await state.set_state(None)


SELL_AMOUNT_PATTERN = re.compile(r"setting:edit_sell_amount_(\d)")


@router.callback_query(lambda c: SELL_AMOUNT_PATTERN.match(c.data))
async def set_sell_amount(callback: CallbackQuery, state: FSMContext):
    if callback.message is None:
        return

    if not isinstance(callback.message, Message):
        return

    if callback.data is None:
        logger.warning("No data found in callback")
        return

    # Extract the copytrade ID from callback data
    match = SELL_AMOUNT_PATTERN.match(callback.data)
    if not match:
        logger.warning("Invalid callback data for copytrade selection")
        return

    idx = int(match.group(1))
    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        setting = await get_setting_from_db(callback.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    if not hasattr(setting, f"custom_sell_amount_{idx}"):
        raise ValueError(f"Invalid sell amount index: {idx}")

    setting = cast(Setting, (await state.get_data()).get("setting"))
    current_amount = getattr(setting, f"custom_sell_amount_{idx}")

    # Send prompt message with force reply
    msg = await callback.message.answer(
        f"👋 请输入卖出百分比(当前 {current_amount * 100}):",
        parse_mode="HTML",
        reply_markup=ForceReply(),
    )

    # Store prompt message details for cleanup
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
        original_message_id=callback.message.message_id,
        original_chat_id=callback.message.chat.id,
        sell_idx=idx,
    )
    await state.set_state(SettingStates.WAITING_FOR_CUSTOM_SELL_PCT)


@router.message(SettingStates.WAITING_FOR_CUSTOM_SELL_PCT)
async def handle_custom_sell_amount(message: Message, state: FSMContext):
    if not message.text:
        return

    try:
        sell_bps = round(float(message.text.strip()), 2)
    except ValueError:
        return await invalid_input_and_request_reinput(
            "❌ 请输入 1-100 的数字",
            message,
            state,
        )

    if sell_bps <= 0 or sell_bps > 100:
        return await invalid_input_and_request_reinput(
            "❌ 请输入正确的数字，取值范围为 0~100",
            message,
            state,
        )

    # 转为小数
    sell_bps = sell_bps / 100
    data = await state.get_data()
    if idx := data.get("sell_idx"):
        sell_idx = int(idx)
    else:
        raise ValueError("Sell index not found")

    setting = cast(Setting, (await state.get_data()).get("setting"))
    if setting is None:
        if message.from_user is None:
            raise ValueError("Setting not found")
        setting = await get_setting_from_db(message.from_user.id)
        await state.update_data(setting=setting)
    if setting is None:
        raise ValueError("Setting not found")

    # Update settings
    if not hasattr(setting, f"custom_sell_amount_{sell_idx}"):
        raise ValueError(f"Invalid sell amount index: {sell_idx}")

    old_value = getattr(setting, f"custom_sell_amount_{idx}")
    if old_value == sell_bps:
        await cleanup_conversation_messages(message, state)
        return

    setattr(setting, f"custom_sell_amount_{idx}", sell_bps)
    await setting_service.set(setting)
    await state.update_data(setting=setting)

    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    await cleanup_conversation_messages(message, state)

    render_data = await render(message, setting)
    await message.bot.edit_message_text(
        chat_id=data["original_chat_id"],
        message_id=data["original_message_id"],
        **render_data,
    )

    await state.set_state(None)
