from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def confirm_keyboard(confirm_callback: str, cancel_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ 确认", callback_data=confirm_callback),
                InlineKeyboardButton(text="❌ 取消", callback_data=cancel_callback),
            ]
        ]
    )


def back_keyboard(back_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ 返回", callback_data=back_callback),
            ]
        ]
    )


def cancel_keyboard(cancel_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ 取消", callback_data=cancel_callback),
            ]
        ]
    )
