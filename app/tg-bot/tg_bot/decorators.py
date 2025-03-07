"""Telegram bot decorators."""

import functools
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from aiogram.fsm.context import FSMContext

T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def clear_state(func: T) -> T:
    """
    装饰器：在函数执行完成后清空 state。

    注意：被装饰的函数必须有 state: FSMContext 参数。

    用法：
    @clear_state
    async def handler(message: Message, state: FSMContext):
        ...
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 从参数中找到 FSMContext 实例
        state = None
        for arg in args:
            if isinstance(arg, FSMContext):
                state = arg
                break
        if state is None:
            state = kwargs.get("state")

        if state is None:
            raise ValueError(
                f"Function {func.__name__} must have a state parameter of type FSMContext"
            )

        try:
            # 执行原函数
            result = await func(*args, **kwargs)
            # 清空 state
            await state.clear()
            return result
        except Exception as e:
            # 发生异常时也要清空 state
            await state.clear()
            raise e

    return cast(T, wrapper)
