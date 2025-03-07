from aiogram.types import Message
from solbot_common.log import logger

from .render import render


async def setting_command(message: Message):
    if message.from_user is None:
        logger.warning("No message found in update")
        return

    data = await render(message)
    await message.answer(**data)
