from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from loguru import logger

from tg_bot.services.user import UserService


class InitializeMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            from_user = event.from_user
            if from_user is None:
                logger.warning("Message from user is None")
                return
            if event.text == "/start":
                logger.info("User {user_id} initialized")
                return await handler(event, data)
            user_id = from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            logger.warning("Unknown event type")
            return

        user_service = UserService()
        is_registered = await user_service.is_registered(user_id)
        if not is_registered:
            logger.warning(f"User {user_id} is not registered")
            await event.answer("⚠️  您还未初始化账户，请先点击 /start 初始化")
            return

        return await handler(event, data)
