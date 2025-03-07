from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from solbot_common.types.bot_setting import BotSetting as Setting


def get_token_keyboard(setting: Setting, mint: str) -> InlineKeyboardMarkup:
    """获取代币交易键盘布局"""
    keyboard = []

    # 第一行：现价、挂单、刷新
    keyboard.append(
        [
            InlineKeyboardButton(
                text="✅ 现价" if True else "❌ 现价",  # TODO: 暂时只支持现价
                callback_data="toggle_price",
            ),
            # InlineKeyboardButton(text="挂单", callback_data="pending_orders"),
            InlineKeyboardButton(text="刷新", callback_data=f"swap:refresh_{mint}"),
        ]
    )

    # 第二行：快速模式和防夹模式
    keyboard.append(
        [
            InlineKeyboardButton(
                text=f"🚀 快速模式 {'✅' if setting.auto_slippage else '❌'}",
                callback_data="toggle_quick_mode",
            ),
            InlineKeyboardButton(
                text=f"🛡️ 防夹模式 {'✅' if setting.sandwich_mode else '❌'}",
                callback_data="toggle_sandwich_mode",
            ),
        ]
    )

    # 分隔线：买
    keyboard.append([InlineKeyboardButton(text="----- 买 -----", callback_data="separator_buy")])

    # 买入金额按钮（两行）
    keyboard.append(
        [
            InlineKeyboardButton(
                text=f"🟢买 {setting.custom_buy_amount_1} SOL",
                callback_data=f"buy_{setting.custom_buy_amount_1}_{mint}",
            ),
            InlineKeyboardButton(
                text=f"🟢买 {setting.custom_buy_amount_2} SOL",
                callback_data=f"buy_{setting.custom_buy_amount_2}_{mint}",
            ),
            InlineKeyboardButton(
                text=f"🟢买 {setting.custom_buy_amount_3} SOL",
                callback_data=f"buy_{setting.custom_buy_amount_3}_{mint}",
            ),
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                text=f"🟢买 {setting.custom_buy_amount_4} SOL",
                callback_data=f"buy_{setting.custom_buy_amount_4}_{mint}",
            ),
            InlineKeyboardButton(
                text=f"🟢买 {setting.custom_buy_amount_5} SOL",
                callback_data=f"buy_{setting.custom_buy_amount_5}_{mint}",
            ),
            InlineKeyboardButton(text="🟢买 x SOL", callback_data=f"buyx_{mint}"),
        ]
    )

    # 分隔线：卖
    keyboard.append([InlineKeyboardButton(text="----- 卖 -----", callback_data="separator_sell")])

    # 卖出比例按钮
    keyboard.append(
        [
            InlineKeyboardButton(
                text=f"🔴卖 {setting.custom_sell_amount_1 * 100}%",
                callback_data=f"sell_{setting.custom_sell_amount_1 * 100}_{mint}",
            ),
            InlineKeyboardButton(
                text=f"🔴卖 {setting.custom_sell_amount_2 * 100}%",
                callback_data=f"sell_{setting.custom_sell_amount_2 * 100}_{mint}",
            ),
            InlineKeyboardButton(text="🔴卖 x%", callback_data=f"sell_custom_{mint}"),
        ]
    )

    # 一键回本按钮
    # keyboard.append(
    #     [InlineKeyboardButton(text="🔴一键回本", callback_data="sell_breakeven")]
    # )

    # 底部按钮：返回、设置、分享晒单图
    keyboard.append(
        [
            InlineKeyboardButton(text="返回", callback_data="back_to_home"),
            InlineKeyboardButton(text="设置", callback_data="set"),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
