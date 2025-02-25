import asyncio
import base64
from typing import TypedDict, cast

import aioredis
import orjson as json
from solana.rpc import commitment
from solana.rpc.async_api import AsyncClient
from solana.rpc.websocket_api import connect
from solders.pubkey import Pubkey
from solders.rpc.responses import ProgramNotification
from sqlmodel import select
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from cache.auto.base import AutoUpdateCacheProtocol
from common.config import settings
from common.constants import RAY_V4, WSOL
from common.layouts.amm_v4 import LIQUIDITY_STATE_LAYOUT_V4
from common.log import logger
from common.models.raydium_pool import RaydiumPoolModel
from common.utils.pool import AmmV4PoolKeys
from common.utils.raydium import RaydiumAPI
from common.utils.utils import get_async_client
from db.redis import RedisClient
from db.session import NEW_ASYNC_SESSION, provide_session, start_async_session


class MintPoolPriorityQueue:
    def __init__(
        self,
        redis_client,
        max_length=10,
    ):
        """为每个 Mint 维护一个优先级队列，用于存储和排序其流动性池

        每个 Mint 可能在多个 AMM 中都有流动性池，此类用于管理这些池子的优先级排序。
        优先级越高的池子，流动性和使用频率越高。

        Args:
            redis_client: Redis客户端实例
            max_length: 每个 Mint 最多保留的池子数量，默认10个
        """
        self.redis = redis_client
        self.max_length = max_length
        self._prefix = "raydium_pool:pool_sorter"

    async def push(self, mint: str, pool_id: str):
        """添加或更新池子的优先级

        Args:
            mint: Mint 地址
            pool_id: 流动性池的ID
        """
        # 检查元素是否已存在
        current_score = await self.redis.zscore(f"{self._prefix}:{mint}", pool_id)
        if current_score is not None:
            # 如果存在，优先级+1
            priority = current_score + 1
        else:
            priority = 1

        # 添加或更新元素到队列
        await self.redis.zadd(f"{self._prefix}:{mint}", {pool_id: priority})
        # 维持队列长度
        await self.trim_queue(f"{self._prefix}:{mint}")

    async def pop(self, mint: str):
        """获取并移除优先级最高的池子

        Args:
            queue_key: Mint 地址作为队列键

        Returns:
            tuple: (pool_id, priority) 或 None
        """
        result = await self.redis.zpopmax(f"{self._prefix}:{mint}", count=1)
        if result:
            return result[0]  # 返回 (pool_id, priority) 元组
        return None

    async def get(self, mint: str, pool_id: str):
        """获取指定池子的优先级，并将其优先级+1

        Args:
            queue_key: Mint 地址作为队列键
            pool_id: 流动性池的ID

        Returns:
            float: 更新后的优先级，如果池子不存在则返回 None
        """
        current_score = await self.redis.zscore(f"{self._prefix}:{mint}", pool_id)
        if current_score is not None:
            # 增加优先级
            await self.redis.zincrby(f"{self._prefix}:{mint}", 1, pool_id)
            return await self.redis.zscore(f"{self._prefix}:{mint}", pool_id)
        return None

    async def get_top_pool(self, mint: str) -> str | None:
        """获取指定代币优先级最高的流动性池（不删除）

        Args:
            mint: 代币的 Mint 地址

        Returns:
            str | None: 优先级最高的池子ID，如果没有则返回 None
        """
        result = await self.redis.zrevrange(
            f"{self._prefix}:{mint}",
            0,  # 获取第一个元素（优先级最高的）
            0,  # 只获取一个元素
            withscores=True,
        )
        if result:
            pool_id, score = result[0]  # 返回 (pool_id, score) 元组
            # 增加使用次数
            await self.redis.zincrby(f"{self._prefix}:{mint}", 1, pool_id)
            return pool_id
        return None

    async def trim_queue(self, mint: str):
        """确保每个 Mint 的池子数量不超过最大限制

        Args:
            queue_key: Mint 地址作为队列键
        """
        current_length = await self.redis.zcard(f"{self._prefix}:{mint}")
        if current_length > self.max_length:
            # 删除多余的元素（保留优先级最高的元素）
            await self.redis.zremrangebyrank(
                f"{self._prefix}:{mint}",
                0,  # 从低优先级开始删除
                current_length - self.max_length - 1,
            )


class AMMData(TypedDict):
    pool_id: Pubkey
    amm_data: bytes
    market_data: bytes


class MintPoolDataCache:
    def __init__(self, redis: aioredis.Redis, max_expiration: int = 60 * 60 * 24 * 7):
        self.redis = redis
        self._prefix = "raydium_pool:pool_data"
        # 最多缓存 5000 个池子的信息
        self.max_expiration = max_expiration

    async def set(self, pool_id: str, pool_data: AMMData):
        encoded = {
            "pool_id": str(pool_data["pool_id"]),
            "amm_data": base64.b64encode(pool_data["amm_data"]).decode("utf-8"),
            "market_data": base64.b64encode(pool_data["market_data"]).decode("utf-8"),
        }
        await self.redis.set(
            f"{self._prefix}:{pool_id}",
            json.dumps(encoded),
            ex=self.max_expiration,
        )

    async def get(self, pool_id: str) -> AMMData | None:
        text = await self.redis.get(f"{self._prefix}:{pool_id}")
        if text is None:
            return None
        data = json.loads(text)
        data["pool_id"] = Pubkey.from_string(data["pool_id"])
        data["amm_data"] = base64.b64decode(data["amm_data"])
        data["market_data"] = base64.b64decode(data["market_data"])
        return data

    async def delete(self, pool_id: str):
        await self.redis.delete(f"{self._prefix}:{pool_id}")


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
                    "Waiting for {} tasks to complete...".format(
                        len(self._running_tasks)
                    ),
                )
                # 等待所有正在运行的任务完成
                if self._running_tasks:
                    await asyncio.gather(*self._running_tasks, return_exceptions=True)

            self._running_tasks.clear()

    def is_running(self):
        return len(self._running_tasks) > 0


class RaydiumPoolStoreage:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.pool_sorter = MintPoolPriorityQueue(redis)
        self.pool_data = MintPoolDataCache(redis)

    @provide_session
    async def get_pool_data_by_mint(
        self, mint: str, *, session=NEW_ASYNC_SESSION
    ) -> AMMData | None:
        """获取指定 Mint 的流动性池数据.

        如果池子的缓存不存在，则从数据库中查询

        Args:
            mint: Mint 地址
            session: 数据库会话

        Returns:
            AMMData | None: 流动性池数据，如果池子不存在则返回 None
        """
        top_pool_id = await self.pool_sorter.get_top_pool(mint)
        pool_data: AMMData | None = None
        if top_pool_id is None:
            # 去数据库中查询
            stmt = select(RaydiumPoolModel).where(RaydiumPoolModel.mint == mint)
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if record is not None:
                pool_data = {
                    "pool_id": Pubkey.from_string(record.pool_id),
                    "amm_data": record.amm_data,
                    "market_data": record.market_data,
                }
        else:
            pool_data = (
                await self.pool_data.get(top_pool_id)
                if pool_data is None
                else pool_data
            )
        return pool_data

    async def is_exist(self, pool_id: Pubkey) -> bool:
        """
        是否存在 redis 中，如果存在则返回 True
        """
        return await self.pool_data.get(str(pool_id)) is not None

    async def update(self, pool_id: Pubkey, pool_data: AMMData):
        pool_keys = AmmV4PoolKeys.from_pool_data(
            pool_id, pool_data["amm_data"], pool_data["market_data"]
        )
        mint = (
            pool_keys.base_mint if pool_keys.base_mint != WSOL else pool_keys.quote_mint
        )
        await self.pool_sorter.push(str(mint), str(pool_id))

        await self.pool_data.set(str(pool_id), pool_data)
        # PERF: 没有必要每次都 trim，可以定期执行
        await self.pool_sorter.trim_queue(str(mint))

        async with start_async_session() as session:
            # 检查记录是否存在
            stmt = select(RaydiumPoolModel.id).where(
                RaydiumPoolModel.pool_id == str(pool_id)
            )
            result = await session.execute(stmt)
            pool = result.scalar_one_or_none()

            if pool is None:
                # 不存在则创建新记录
                pool = RaydiumPoolModel(
                    mint=str(mint),
                    pool_id=str(pool_id),
                    amm_data=pool_data["amm_data"],
                    market_data=pool_data["market_data"],
                )
                session.add(pool)

        logger.info(f"Pool data updated: {pool_id}")


async def fetch_pool_data_from_rpc(
    pool_id: Pubkey, rpc_client: AsyncClient
) -> AMMData | None:
    """从 rpc 获取池子信息"""
    resp = await rpc_client.get_account_info_json_parsed(
        pool_id, commitment=commitment.Processed
    )
    if resp.value is None:
        return None
    amm_data = bytes(resp.value.data)
    amm_data_decoded = LIQUIDITY_STATE_LAYOUT_V4.parse(amm_data)
    market_id = Pubkey.from_bytes(amm_data_decoded.serumMarket)

    resp = await rpc_client.get_account_info_json_parsed(
        market_id, commitment=commitment.Processed
    )
    if resp.value is None:
        logger.error(f"Failed to fetch market data: {market_id}， pool_id: {pool_id}")
        return None

    market_data = bytes(resp.value.data)

    return {
        "pool_id": pool_id,
        "amm_data": amm_data,
        "market_data": market_data,
    }


async def get_preferred_pool(mint: Pubkey | str) -> AMMData | None:
    """获取 mint 优先级最高的池子"""
    redis = RedisClient.get_instance()
    storeage = RaydiumPoolStoreage(redis)

    async def _get_pool_data_from_cache(mint: str) -> AMMData | None:
        pool_data = await storeage.get_pool_data_by_mint(mint)
        if pool_data is not None:
            return pool_data
        return None

    async def _get_pool_data_from_rpc(mint: str) -> AMMData | None:
        rpc_client = get_async_client()
        data = await RaydiumAPI().get_pool_info_by_mint(str(mint))
        count = data["count"]
        if count == 0:
            return None
        pool_id = cast(str, data["data"][0]["id"])

        pool_pubkey = Pubkey.from_string(pool_id)
        pool_data = await fetch_pool_data_from_rpc(pool_pubkey, rpc_client)

        if pool_data is not None:
            await storeage.update(pool_pubkey, pool_data)

        return pool_data

    mint_str = str(mint)
    pool_data = await _get_pool_data_from_cache(mint_str)
    if pool_data is None:
        logger.info(f"No pool found for mint: {mint}, fetching from rpc")
        pool_data = await _get_pool_data_from_rpc(mint_str)
    return pool_data


if __name__ == "__main__":
    from db.redis import RedisClient

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
