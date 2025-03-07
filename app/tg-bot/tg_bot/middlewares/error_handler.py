from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from loguru import logger


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception(f"Error in middleware: {e}")

            if (isinstance(event, Message) and event.text is not None) or (
                isinstance(event, CallbackQuery) and event.data is not None
            ):
                await event.answer("❌ 未知错误，请重试！如果问题持续，请联系开发者")
            else:
                logger.warning("Unknown event type")
                return
