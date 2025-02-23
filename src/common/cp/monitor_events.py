"""
Monitor event producer and consumer for handling wallet monitoring events
"""

from enum import Enum
from typing import Callable, Optional

import aioredis
import orjson as json
from aioredis.client import PubSub
from pydantic import BaseModel

from common.log import logger


class MonitorEventType(str, Enum):
    """监听器事件类型"""

    PAUSE = "pause"  # 暂停监听器
    RESUME = "resume"  # 恢复监听器
    RESUME_MANY = 'resume_many'  # 恢复多个监听器


class MonitorEvent(BaseModel):
    """监听器事件"""

    event_type: MonitorEventType
    monitor_id: int
    target_wallet: str
    owner_id: int
    wallet_alias: Optional[str] = None


class MonitorEventProducer:
    """监听器事件生产者"""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.channel = "monitor_events"

    async def publish_event(self, event: MonitorEvent):
        """发布监听器事件"""
        await self.redis.publish(self.channel, json.dumps(event.dict()))

    async def pause_monitor(self, monitor_id: int, target_wallet: str, owner_id: int):
        """暂停监听器

        Args:
            monitor_id: 监听器 id
            target_wallet: 目标钱包
            owner_id: 用户 id
        """
        event = MonitorEvent(
            event_type=MonitorEventType.PAUSE,
            monitor_id=monitor_id,
            target_wallet=target_wallet,
            owner_id=owner_id,
        )
        await self.publish_event(event)
        logger.info(f"Paused monitor {monitor_id} for wallet {target_wallet}")

    async def resume_monitor(self, monitor_id: int, target_wallet: str, owner_id: int):
        """恢复监听器

        Args:
            monitor_id: 监听器 id
            target_wallet: 目标钱包
            owner_id: 用户 id
        """
        event = MonitorEvent(
            event_type=MonitorEventType.RESUME,
            monitor_id=monitor_id,
            target_wallet=target_wallet,
            owner_id=owner_id,
        )
        await self.publish_event(event)
        logger.info(f"Resumed monitor {monitor_id} for wallet {target_wallet}")

    async def resume_many_monitor(self, monitor_id: int, target_wallets: str, owner_id: int):
        """恢复监听器

        Args:
            monitor_id: 监听器 id
            target_wallet: 目标钱包
            owner_id: 用户 id
        """
        event = MonitorEvent(
            event_type=MonitorEventType.RESUME_MANY,
            monitor_id=monitor_id,
            target_wallet=target_wallets,
            owner_id=owner_id,
        )
        await self.publish_event(event)
        logger.info(f"Resumed monitor {monitor_id} for wallet {target_wallets}")

class MonitorEventConsumer:
    """监听器事件消费者

    用于订阅和处理监听器事件的类。支持动态注册和注销事件处理器，以及优雅的停止订阅。

    Attributes:
        redis (aioredis.Redis): Redis客户端实例
        channel (str): 订阅的Redis频道名
        _handlers (dict): 事件处理器映射表
        _pubsub (Optional[aioredis.client.PubSub]): Redis PubSub对象
    """

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.channel = "monitor_events"
        self._handlers: dict[MonitorEventType, Callable] = {}
        self._pubsub: PubSub | None = None

    async def subscribe(self) -> PubSub:
        """订阅监听器事件

        Returns:
            aioredis.client.PubSub: Redis PubSub对象

        Raises:
            RuntimeError: 如果重复调用subscribe
        """
        if self._pubsub is not None:
            raise RuntimeError("Already subscribed to channel")

        self._pubsub = self.redis.pubsub()
        await self._pubsub.subscribe(self.channel)
        return self._pubsub

    async def unsubscribe(self) -> None:
        """取消订阅并清理资源

        Raises:
            RuntimeError: 如果未订阅就调用unsubscribe
        """
        if self._pubsub is None:
            raise RuntimeError("Not subscribed to any channel")

        await self._pubsub.unsubscribe(self.channel)
        await self._pubsub.close()
        self._pubsub = None

    def register_handler(self, event_type: MonitorEventType, handler: Callable) -> None:
        """注册事件处理器

        Args:
            event_type: 事件类型
            handler: 处理器函数，必须是一个接受MonitorEvent参数的异步函数

        Raises:
            ValueError: 如果handler不是可调用对象
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")
        self._handlers[event_type] = handler

    def unregister_handler(self, event_type: MonitorEventType) -> None:
        """注销事件处理器

        Args:
            event_type: 要注销的事件类型
        """
        self._handlers.pop(event_type, None)

    def get_registered_events(self) -> list[MonitorEventType]:
        """获取所有已注册处理器的事件类型

        Returns:
            list[MonitorEventType]: 已注册的事件类型列表
        """
        return list(self._handlers.keys())

    async def process_event(self, message: dict) -> None:
        """处理监听器事件

        Args:
            message: Redis消息对象

        Raises:
            ValueError: 如果消息格式无效
            KeyError: 如果消息缺少必要字段
        """
        if not isinstance(message, dict):
            raise ValueError("Invalid message format: must be a dictionary")

        if message.get("type") != "message":
            return

        try:
            data = message.get("data")
            if not data:
                raise ValueError("Empty message data")

            event_data = json.loads(data)
            event = MonitorEvent(**event_data)

            if handler := self._handlers.get(event.event_type):
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")
                    raise
            else:
                logger.warning(
                    f"No handler registered for event type: {event.event_type}"
                )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message data: {e}")
            raise ValueError(f"Invalid JSON format: {e}") from e
        except Exception as e:
            logger.error(f"Error processing monitor event: {e}")
            raise
