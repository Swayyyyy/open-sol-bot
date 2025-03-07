from aiogram import types
from solbot_common.log import logger
from solbot_services.bot_setting import BotSettingService as SettingService

from tg_bot.services.user import UserService
from tg_bot.utils.setting import get_wallet

from .render import render

user_service = UserService()
setting_service = SettingService()


async def asset(message: types.Message):
    if message.from_user is None:
        raise ValueError("User is None")
    try:
        wallet = await get_wallet(message.from_user.id)
        render_data = await render(wallet)
    except Exception as e:
        logger.exception(e)
        await message.answer("❌ 获取资产列表失败，请重试")
        return
    await message.answer(**render_data)
