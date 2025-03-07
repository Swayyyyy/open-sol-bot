import asyncio

import aioredis
from solana.rpc import commitment
from solana.rpc.websocket_api import connect
from solbot_cache.rayidum import RaydiumPoolStoreage
from solbot_common.config import settings
from solbot_common.constants import RAY_V4
from solbot_common.layouts.amm_v4 import LIQUIDITY_STATE_LAYOUT_V4
from solbot_common.log import logger
from solbot_common.utils.pool import fetch_pool_data_from_rpc
from solbot_common.utils.utils import get_async_client
from solbot_db.redis import RedisClient
from solders.rpc.responses import ProgramNotification  # type: ignore
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from cache_preloader.core.base import AutoUpdateCacheProtocol


class RaydiumPoolCache(AutoUpdateCacheProtocol):
    def __init__(
        self,
        rpc_endpoint: str,
        redis: aioredis.Redis,
        max_concurrent_tasks: int = 10,
    ):
        self.rpc_client = get_async_client()
        self.websocket_url = rpc_endpoint.replace("https://", "wss://")
        self.storeage = RaydiumPoolStoreage(redis)
        # 添加信号量来限制并发任务数
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        # 用于追踪正在运行的任务
        self._running_tasks: set[asyncio.Task] = set()
        # 是否处于等待其他任务完成的标志
        self._waiting_for_tasks = False

    async def _process_message(self, message: ProgramNotification):
        """使用信号量包装消息处理函数"""
        try:
            async with self._semaphore:
                await self._handle_message(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.exception(e)
        finally:
            # 从正在运行的任务集合中移除当前任务
            current_task = asyncio.current_task()
            if current_task:
                self._running_tasks.discard(current_task)

    async def _handle_message(self, message: ProgramNotification):
        pool_id = message.result.value.pubkey
        is_exists = await self.storeage.is_exist(pool_id)
        if is_exists:
            logger.debug(f"Pool data already exists: {pool_id}")
            return

        try:
            pool_data = await fetch_pool_data_from_rpc(pool_id, self.rpc_client)
        except Exception as e:
            logger.exception(f"Error fetching market data: {e}")
            return

        if pool_data is None:
            logger.error(f"Failed to fetch pool data for pool_id: {pool_id}")
            return

        await self.storeage.update(pool_id, pool_data)

    async def start(self):
        try:
            async with connect(
                self.websocket_url,
                ping_timeout=30,
                ping_interval=20,
                close_timeout=20,
            ) as websocket:
                self.websocket = websocket
                await self.websocket.program_subscribe(
                    program_id=RAY_V4,
                    commitment=commitment.Confirmed,
                    encoding="jsonParsed",
                    filters=[LIQUIDITY_STATE_LAYOUT_V4.sizeof()],
                )

                while True:
                    try:
                        messages = await websocket.recv()
                        for message in messages:
                            if not isinstance(message, ProgramNotification):
                                continue
                            # 创建新任务并追踪它
                            task = asyncio.create_task(self._process_message(message))
                            self._running_tasks.add(task)
                            logger.debug(f"Current tasks: {len(self._running_tasks)}")
                    except (ConnectionClosedError, ConnectionClosedOK) as ws_error:
                        logger.warning(f"WebSocket connection closed: {ws_error}")
                        break
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        logger.exception(e)
                        break
        except Exception as e:
            logger.error(f"Error in start: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """停止所有正在运行的任务"""
        logger.info("Stopping RaydiumPoolCache...")

        if hasattr(self, "websocket"):
            await self.websocket.close()

        logger.info("RaydiumPoolCache Websocket closed")

        if hasattr(self, "_running_tasks"):
            if self._waiting_for_tasks is True and len(self._running_tasks) != 0:
                # Force all tasks to complete
                for task in self._running_tasks:
                    task.cancel()
            else:
                self._waiting_for_tasks = True
                logger.info(
                    f"Waiting for {len(self._running_tasks)} tasks to complete...",
                )
                # 等待所有正在运行的任务完成
                if self._running_tasks:
                    await asyncio.gather(*self._running_tasks, return_exceptions=True)

            self._running_tasks.clear()

    def is_running(self):
        return len(self._running_tasks) > 0


if __name__ == "__main__":
    from solbot_db.redis import RedisClient

    async def main():
        redis = RedisClient.get_instance()
        pool = RaydiumPoolCache(settings.rpc.rpc_url, redis)

        try:
            await pool.start()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            await pool.stop()

    asyncio.run(main())
