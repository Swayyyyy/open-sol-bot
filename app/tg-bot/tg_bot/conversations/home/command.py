from datetime import datetime

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from solbot_cache.token_info import TokenInfoCache
from solbot_common.config import settings
from solbot_common.log import logger
from solbot_services.bot_setting import BotSettingService as SettingService

from tg_bot.conversations.swap.render import render as render_swap
from tg_bot.keyboards.main_menu import main_menu_keyboard
from tg_bot.services.activation import ActivationCodeService
from tg_bot.services.user import UserService
from tg_bot.templates import render_first_use_message
from tg_bot.utils import generate_keypair

from .render import render

user_service = UserService()
setting_service = SettingService()
activation_code_service = ActivationCodeService()


async def _start(message: types.Message):
    """Send a message when the command /start is issued."""
    if message.from_user is None:
        logger.error("Message from None")
        return
    registered = await user_service.is_registered(message.from_user.id)
    if registered:
        data = await render(message)
        await message.answer(**data)
    else:
        # 生成钱包
        keypair = generate_keypair()
        pubkey = keypair.pubkey()
        wallet_address = pubkey.__str__()

        await user_service.register(
            message.from_user.id,
            keypair,
        )

        # 生成默认配置
        await setting_service.create_default(
            chat_id=message.from_user.id,
            wallet_address=wallet_address,
        )

        expiration_datetime = None
        if settings.tg_bot.mode == "private":
            remaining_time = await activation_code_service.get_user_expired_timestamp(
                message.from_user.id
            )
            # -> 年-月-日 时:分:秒
            expiration_datetime = datetime.fromtimestamp(remaining_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        text = render_first_use_message(
            mention=message.from_user.mention_html(),
            wallet_address=wallet_address,
            expiration_datetime=expiration_datetime,
        )
        await message.answer(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard(),
        )


async def start_asset(token_mint: str, message: types.Message, state: FSMContext):
    logger.info(f"Starting asset {token_mint}")
    setting_service = SettingService()
    user_service = UserService()
    token_info_cache = TokenInfoCache()

    # TODO: validate token mint

    if message.from_user is None:
        raise ValueError("User not found")

    chat_id = message.from_user.id
    wallet = await user_service.get_pubkey(chat_id)
    setting = await setting_service.get(chat_id, wallet)
    if setting is None:
        raise ValueError(f"Setting not found, chat_id: {chat_id}, wallet: {wallet}")

    token_info = await token_info_cache.get(token_mint)
    if token_info is None:
        logger.info(f"No token info found for {token_mint}")
        await message.answer("❌ 无法查询到该代币信息")
        return
    logger.info(f"New Found Token Info: {token_info}")

    await state.update_data(setting=setting, token_info=token_info, wallet=wallet)

    data = render_swap(token_info=token_info, setting=setting)
    await message.answer(**data)


async def start(message: types.Message, state: FSMContext):
    """Send a message when the command /start is issued."""
    if message.from_user is None:
        logger.error("Message from None")
        return

    if message.text is None:
        logger.warning("No text found in message")
        return

    text = message.text.strip()
    if text == "/start":
        await _start(message)
        return

    try:
        _, arg = text.split(" ", 1)
    except ValueError:
        await _start(message)
        return

    if arg.startswith("asset_"):
        # https://t.me/hello_trading_bot?start=asset_xxxx
        token_mint = arg.split("_")[1]
        await start_asset(token_mint, message, state)
    else:
        token_info_cache = TokenInfoCache()
        token_info = await token_info_cache.get(arg)
        if token_info is None:
            await message.answer("❌ 无法查询到该代币信息")
            return
        await start_asset(token_info.mint, message, state)
