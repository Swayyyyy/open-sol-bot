from datetime import datetime

from aiogram import types
from aiogram.enums import ParseMode
from solbot_cache.wallet import WalletCache
from solbot_common.config import settings
from solbot_common.utils.shyft import ShyftAPI

from tg_bot.keyboards.main_menu import main_menu_keyboard
from tg_bot.services.activation import ActivationCodeService
from tg_bot.services.user import UserService
from tg_bot.templates import render_start_message

shyft = ShyftAPI(settings.api.shyft_api_key)
user_service = UserService()
wallet_cache = WalletCache()
activation_code_service = ActivationCodeService()


async def render(update: types.Message | types.CallbackQuery) -> dict:
    """渲染主页消息

    Args:
        update: 可以是 Message（用户发送 /start）或 CallbackQuery（用户点击返回按钮）
    """
    # 获取用户信息
    if isinstance(update, types.CallbackQuery):
        # 从回调查询中获取用户信息
        user = update.from_user
    else:
        # 从消息中获取用户信息
        user = update.from_user

    if user is None:
        raise ValueError("User is None")

    mention = user.mention_html() if user else "null"
    wallet_address = await user_service.get_pubkey(user.id)
    balance = await wallet_cache.get_sol_balance(wallet_address)

    expiration_datetime = None
    if settings.tg_bot.mode == "private":
        remaining_time = await activation_code_service.get_user_expired_timestamp(user.id)
        # -> 年-月-日 时:分:秒
        expiration_datetime = datetime.fromtimestamp(remaining_time).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "text": render_start_message(
            mention=mention,
            wallet_address=wallet_address,
            balance=balance,
            expiration_datetime=expiration_datetime,
        ),
        "parse_mode": ParseMode.HTML,
        "reply_markup": main_menu_keyboard(),
    }
