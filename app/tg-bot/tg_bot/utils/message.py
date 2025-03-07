"""Message handling utility functions."""

import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import ForceReply, Message
from solbot_common.log import logger


async def cleanup_conversation_messages(message: Message, state: FSMContext):
    """
    Clean up both the user's input message and the bot's prompt message in a conversation.

    Args:
        message (Message): The message to be deleted (usually user's input)
        state (FSMContext): The FSM context containing prompt message information
    """
    data = await state.get_data()
    if message.bot is None:
        logger.warning("No bot found in message")
        return

    # Clean up messages
    try:
        await message.delete()  # Delete user's input
        await message.bot.delete_message(  # Delete prompt message
            chat_id=data["prompt_chat_id"],
            message_id=data["prompt_message_id"],
        )
    except Exception as e:
        logger.warning(f"Failed to delete messages: {e}")
        raise e


# 数据校验失败并要求用户重新输入
async def invalid_input_and_request_reinput(text: str, last_message: Message, state: FSMContext):
    msg = await last_message.answer(text, reply_markup=ForceReply())
    await cleanup_conversation_messages(last_message, state)
    await state.update_data(
        prompt_message_id=msg.message_id,
        prompt_chat_id=msg.chat.id,
    )
    return


async def delete_later(message: Message, delay: int = 5):
    """
    Delete a message after a specified delay.

    Args:
        message (Message): The message to delete
        delay (int, optional): Delay in seconds before deletion. Defaults to 5.
    """

    async def _delete_later():
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception as e:
            # 如果删除消息失败，可能是消息已经被删除，或者消息不存在
            logger.warning("Error deleting message: {}", e)

    delete_task = asyncio.create_task(_delete_later())
    # 添加任务完成回调以处理可能的异常
    delete_task.add_done_callback(lambda t: t.exception() if t.exception() else None)
