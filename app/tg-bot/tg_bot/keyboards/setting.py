from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from solbot_common.types.bot_setting import BotSetting as Setting


def settings_keyboard(setting: Setting) -> InlineKeyboardMarkup:
    # 自动滑点按钮文本
    auto_slippage_text = "✅ 自动滑点开启" if setting.auto_slippage else "❌ 自动滑点关闭"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=auto_slippage_text,
                    callback_data="setting:toggle_auto_slippage",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=(
                        f"快速滑点 {setting.get_quick_slippage_pct()}% ✏️"
                        if setting.auto_slippage
                        else f"✅ 快速滑点 {setting.get_quick_slippage_pct()}% ✏️"
                    ),
                    callback_data="setting:edit_quick_slippage",
                ),
                InlineKeyboardButton(
                    text=f"防夹滑点 {setting.get_sandwich_slippage_pct()}% ✏️",
                    callback_data="setting:edit_sandwich_slippage",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="修改买入优先费",
                    callback_data="setting:edit_buy_priority_fee",
                ),
                InlineKeyboardButton(
                    text="修改卖出优先费",
                    callback_data="setting:edit_sell_priority_fee",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ 自动买开启" if setting.auto_buy else "❌ 自动买关闭",
                    callback_data="setting:toggle_auto_buy",
                ),
                InlineKeyboardButton(
                    text="✅ 自动卖开启" if setting.auto_sell else "❌ 自动卖关闭",
                    callback_data="setting:toggle_auto_sell",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="----- 自定义买 -----",
                    callback_data="setting:custom_buy_divider",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{setting.custom_buy_amount_1} SOL ✏️",
                    callback_data="setting:edit_buy_amount_1",
                ),
                InlineKeyboardButton(
                    text=f"{setting.custom_buy_amount_2} SOL ✏️",
                    callback_data="setting:edit_buy_amount_2",
                ),
                InlineKeyboardButton(
                    text=f"{setting.custom_buy_amount_3} SOL ✏️",
                    callback_data="setting:edit_buy_amount_3",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{setting.custom_buy_amount_4} SOL ✏️",
                    callback_data="setting:edit_buy_amount_4",
                ),
                InlineKeyboardButton(
                    text=f"{setting.custom_buy_amount_5} SOL ✏️",
                    callback_data="setting:edit_buy_amount_5",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="----- 自定义卖 -----",
                    callback_data="setting:custom_sell_divider",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{setting.custom_sell_amount_1 * 100}% ✏️",
                    callback_data="setting:edit_sell_amount_1",
                ),
                InlineKeyboardButton(
                    text=f"{setting.custom_sell_amount_2 * 100}% ✏️",
                    callback_data="setting:edit_sell_amount_2",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ 返回",
                    callback_data="back_to_home",
                )
            ],
        ]
    )
