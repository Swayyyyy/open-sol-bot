import asyncio
import re

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from common.config import settings
from common.prestart import pre_start
from db.redis import RedisClient
from loguru import logger

from tg_bot.conversations import (
    admin,
    asset,
    copytrade,
    home,
    monitor,
    setting,
    swap,
    wallet,
)
from tg_bot.conversations.router import router
from tg_bot.conversations.states import CopyTradeStates, MonitorStates, WalletStates
from tg_bot.middlewares import (
    AuthorizationMiddleware,
    DebugMiddleware,
    ErrorHandlerMiddleware,
    InitializeMiddleware,
)
from tg_bot.notify.notify import Notify


async def get_chat_id(message):
    await message.answer(f"您的 chat id 是: <code>{message.chat.id}</code>")


async def start_bot():
    """Start the bot."""
    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register middlewares
    middlewares = [
        InitializeMiddleware,
        AuthorizationMiddleware,
        DebugMiddleware,
        ErrorHandlerMiddleware,
    ]
    for middleware in middlewares:
        dp.message.middleware(middleware())
        dp.callback_query.middleware(middleware())

    # Register handlers
    dp.message.register(home.start_command, Command("start"))
    dp.message.register(copytrade.copytrade_command, Command("copytrade"))
    dp.message.register(monitor.monitor_command, Command("monitor"))
    dp.message.register(setting.setting_command, Command("set"))
    dp.message.register(wallet.wallet_command, Command("wallet"))
    dp.message.register(asset.asset_command, Command("asset"))
    excluded_states = [
        CopyTradeStates.CREATE_WAITING_FOR_ADDRESS,
        CopyTradeStates.EDIT_WAITING_FOR_ADDRESS,
        MonitorStates.CREATE_WAITING_FOR_ADDRESS,
        WalletStates.WAITING_FOR_NEW_PRIVATE_KEY,
    ]
    dp.message.register(
        swap.info_command,
        F.text.regexp(r"^[a-zA-Z0-9]{43,44}$"),
        ~StateFilter(*excluded_states),
    )
    dp.message.register(
        swap.swap_command, Command(re.compile(r"^buy.*"), re.compile(r"^sell.*"))
    )
    # Admin commands
    dp.message.register(
        admin.generate_activation_code,
        Command(re.compile(r"^generate_activation_code.*")),
    )
    dp.message.register(get_chat_id, Command("chat_id"))
    dp.include_router(router)

    # Starting notify service
    logger.info("Starting notify service...")
    redis = RedisClient.get_instance()
    notify = Notify(redis=redis, bot=bot)
    await notify.start()

    # Start polling
    logger.info("Starting bot...")
    await dp.start_polling(bot)

    # 清理数据库连接
    # await cleanup_session_factory()
    # 关闭 bot
    await bot.session.close()
    await dp.storage.close()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    logger.info(f"Cancelling {len(tasks)} tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Shutdown complete")


if __name__ == "__main__":
    pre_start()
    asyncio.run(start_bot())
