from aiogram.types import Message

from common.config import settings
from common.log import logger
from tg_bot.services.activation import ActivationCodeService


async def generate_activation_code(message: Message):
    if message.from_user is None:
        return

    if message.text is None:
        return

    user_id = message.from_user.id
    if user_id != settings.tg_bot.manager_id:
        logger.warning(f"User {user_id} is not manager")
        message.answer("❌ 你不是管理员，无法执行此操作")
        return

    text = message.text.strip()
    if not text.startswith("/generate_activation_code"):
        return

    try:
        _, expired_in_days = text.split(" ", 1)
        expired_in_days = int(expired_in_days)
    except ValueError:
        expired_in_days = 7

    seconds = expired_in_days * 24 * 60 * 60
    code = await ActivationCodeService().generate_code(seconds)
    logger.info(f"User {user_id} generate activation code: {code}")
    await message.answer(
        f"✅ 激活码: <code>{code}</code>(点击复制) ({expired_in_days} 天)"
    )
