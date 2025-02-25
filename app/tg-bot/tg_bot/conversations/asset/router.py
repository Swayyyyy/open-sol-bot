from aiogram import F, Router, types

from common.log import logger
from tg_bot.utils.setting import get_wallet

from .render import render

router = Router()


@router.callback_query(F.data == "asset")
@router.callback_query(F.data == "asset:refresh")
async def asset(callback: types.CallbackQuery):
    if callback.message is None:
        logger.warning("No message found in update")
        return

    if not isinstance(callback.message, types.Message):
        logger.warning("Message is not a Message object")
        return

    try:
        wallet = await get_wallet(callback.from_user.id)
        render_data = await render(wallet)
    except Exception as e:
        logger.exception(e)
        await callback.answer("❌ 获取资产列表失败，请重试")
        return
    await callback.message.edit_text(**render_data)
