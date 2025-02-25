from aiogram import enums, types

from tg_bot.keyboards.setting import settings_keyboard
from common.types.bot_setting import BotSetting as Setting
from services.bot_setting import BotSettingService as SettingService
from tg_bot.services.user import UserService
from tg_bot.templates import render_setting_message

user_service = UserService()


async def render(
    callback: types.CallbackQuery | types.Message, setting: Setting | None = None
) -> dict:
    s = SettingService()
    if isinstance(callback, types.CallbackQuery):
        chat_id = callback.from_user.id
    elif isinstance(callback, types.Message):
        message = callback
        if message.from_user is None:
            raise ValueError("Message from None")
        chat_id = message.from_user.id

    wallet_address = await user_service.get_pubkey(chat_id)
    if setting is None:
        setting = await s.get(chat_id=chat_id, wallet_address=wallet_address)
    if setting is None:
        raise ValueError("Setting not found")

    text = render_setting_message(setting)
    keyboard = settings_keyboard(setting)
    return {
        "text": text,
        "parse_mode": enums.ParseMode.HTML,
        "reply_markup": keyboard,
    }
