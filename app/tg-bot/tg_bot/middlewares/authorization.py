from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from loguru import logger
from solbot_common.config import settings

from tg_bot.services.activation import ActivationCodeService


class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if settings.tg_bot.mode != "private":
            return await handler(event, data)

        if event.from_user is None:
            return await handler(event, data)

        user_id = event.from_user.id

        if settings.tg_bot.manager_id == user_id:
            return await handler(event, data)

        if event.from_user is None:
            logger.warning("No user found in message")
            return

        # 如果是有激活码，则验证激活码是否有效
        # 如果是无激活码，则直接要求用户输入激活码
        if isinstance(event, Message) and event.text is not None:
            message = event
            text = event.text.strip()
            if text == "/chat_id" or text[0] != "/":
                return await handler(event, data)
        elif isinstance(event, CallbackQuery) and event.data is not None:
            message = event.message
            if event.data == "start:activation_code":
                return await handler(event, data)
        else:
            logger.warning("Unknown event type")
            return

        assert message is not None
        activation_code_service = ActivationCodeService()
        user_license = await activation_code_service.get_user_license(user_id)
        passed = False
        if user_license is None:
            await message.answer(
                "这是一个私有机器人，请输入激活码以继续使用。\n如需获取激活码，请联系管理员。",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="输入激活码",
                                callback_data="start:activation_code",
                            )
                        ]
                    ]
                ),
            )
        else:
            authorized = await activation_code_service.is_user_authorized(user_id)
            if authorized is False:
                await message.answer(
                    "❌ 激活码无效或已过期，请重试或联系管理员获取新的激活码。",
                )
            passed = True

        if passed:
            return await handler(event, data)
