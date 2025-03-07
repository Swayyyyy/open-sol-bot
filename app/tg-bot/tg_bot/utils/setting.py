from solbot_common.types.bot_setting import BotSetting as Setting
from solbot_services.bot_setting import BotSettingService as SettingService

from tg_bot.services.user import UserService

user_service = UserService()
setting_service = SettingService()


async def get_setting_from_db(chat_id: int) -> Setting | None:
    wallet_address = await user_service.get_pubkey(chat_id=chat_id)
    setting = await setting_service.get(
        chat_id=chat_id,
        wallet_address=wallet_address,
    )
    return setting


async def get_wallet(chat_id: int) -> str:
    wallet_address = await user_service.get_pubkey(chat_id=chat_id)
    return wallet_address
