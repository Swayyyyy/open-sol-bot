import httpx
from solbot_common.config import settings

# {
#     "ok": true,
#     "result": {
#         "id": 7087967551,
#         "is_bot": true,
#         "first_name": "MyTradeBot",
#         "username": "hello_trading_bot",
#         "can_join_groups": true,
#         "can_read_all_group_messages": false,
#         "supports_inline_queries": false,
#         "can_connect_to_business": false,
#         "has_main_web_app": false,
#     },
# }


def get_bot_name() -> str:
    api_key = settings.tg_bot.token

    bot_name = None
    with httpx.Client() as session:
        response = session.get(f"https://api.telegram.org/bot{api_key}/getMe")
        if response.status_code == 200:
            data = response.json()
            if data["ok"]:
                bot_name = data["result"]["username"]

    if bot_name is None:
        raise ValueError("Failed to get bot username")

    return bot_name
