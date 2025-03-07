from aiogram import types
from solbot_common.log import logger
from solbot_services.bot_setting import BotSettingService as SettingService

from tg_bot.services.user import UserService

from .render import render

user_service = UserService()
setting_service = SettingService()


async def wallet_command(message: types.Message):
    """Send a message when the command /start is issued."""
    if message.from_user is None:
        logger.error("Message from None")
        return

    data = await render(message)
    await message.answer(**data)
