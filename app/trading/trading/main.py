import asyncio
import time

import backoff
import httpx
from solbot_common.cp.swap_event import SwapEventConsumer
from solbot_common.cp.swap_result import SwapResultProducer
from solbot_common.log import logger
from solbot_common.prestart import pre_start
from solbot_common.types.swap import SwapEvent, SwapResult
from solbot_common.utils.utils import get_async_client
from solbot_db.redis import RedisClient
from solders.signature import Signature  # type: ignore

from trading.copytrade import CopyTradeProcessor
from trading.executor import TradingExecutor
from trading.settlement import SwapSettlementProcessor

import base64
import json
import requests
from solders.pubkey import Pubkey  # type: ignore
from solana.rpc.api import Client
from solders.transaction import VersionedTransaction  # type: ignore
from solders.keypair import Keypair  # type: ignore

class Trading:
    def __init__(self):
        self.redis = RedisClient.get_instance()
        self.rpc_client = get_async_client()
        self.trading_executor = TradingExecutor(self.rpc_client)
        self.swap_settlement_processor = SwapSettlementProcessor()
        # 创建多个消费者实例
        self.num_consumers = 3  # 可以根据需要调整消费者数量
        self.swap_event_consumers = []
        for i in range(self.num_consumers):
            consumer = SwapEventConsumer(
                self.redis,
                "trading:swap_event",
                f"trading:new_swap_event:{i}",  # 为每个消费者创建唯一的名称
            )
            consumer.register_callback(self._process_swap_event)
            self.swap_event_consumers.append(consumer)

        self.copytrade_processor = CopyTradeProcessor()

        self.swap_result_producer = SwapResultProducer(self.redis)
        # 添加任务池和信号量
        self.task_pool = set()
        self.max_concurrent_tasks = 10
        self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

    async def _process_single_swap_event(self, swap_event: SwapEvent):
        """处理单个交易事件的核心逻辑"""
        async with self.semaphore:
            logger.info(f"Processing swap event: {swap_event}")

            try:
                sig = await self._execute_swap(swap_event)
                swap_result = await self._record_swap_result(sig, swap_event)
                logger.info(f"Successfully processed swap event: {swap_event}")
                return swap_result
            except (httpx.ConnectTimeout, httpx.ConnectError):
                logger.error("Connection error")
                await self._record_failed_swap(swap_event)
                return
            except Exception as e:
                logger.exception(f"Failed to process swap event: {swap_event}")
                # 即使发生错误也要记录结果
                await self._record_failed_swap(swap_event)
                raise e

    @backoff.on_exception(
        backoff.expo,
        (httpx.ConnectTimeout, httpx.ConnectError),
        max_tries=3,
        base=1.5,
        factor=0.1,
        max_time=2,
    )
    async def _execute_swap(self, swap_event: SwapEvent) -> Signature | None:
        """执行交易并返回签名"""
        sig = await self.trading_executor.exec(swap_event)
        logger.info(f"Transaction submitted: {sig}")
        return sig

    @backoff.on_exception(
        backoff.expo,
        (httpx.ConnectTimeout, httpx.ConnectError),
        max_tries=2,
        base=1.5,
        factor=0.1,
        max_time=2,
    )
    async def _record_swap_result(self, sig: Signature | None, swap_event: SwapEvent) -> SwapResult:
        """记录交易结果"""
        if not sig:
            return await self._record_failed_swap(swap_event)

        swap_record = await self.swap_settlement_processor.process(sig, swap_event)

        swap_result = SwapResult(
            swap_event=swap_event,
            swap_record=swap_record,
            user_pubkey=swap_event.user_pubkey,
            transaction_hash=str(sig),
            submmit_time=int(time.time()),
        )

        await self.swap_result_producer.produce(swap_result)
        logger.info(f"Recorded transaction: {sig}")
        return swap_result
    
    async def _send_limit_order(self, SwapResult, ratio: float=2) -> None:
        """发送限价订单"""
        pass
    
    def main(self, swap_event: SwapEvent, ratio=2) -> None:
        # 设置Solana RPC连接（根据需要替换为你的RPC节点地址）
        ## TODO
        # 定义Mint地址
        input_mint_addr = swap_event.input_mint
        output_mint_addr = swap_event.output_mint
        output_mint = Pubkey.from_string(input_mint_addr)
        input_mint = Pubkey.from_string(output_mint_addr)
        
        # 获取账户信息，提取owner字段（Token程序地址）
        input_info = self.rpc_client.get_account_info(input_mint)
        output_info = self.rpc_client.get_account_info(output_mint)
        
        # 检查账户信息是否正确获取
        if input_info["result"]["value"] is None or output_info["result"]["value"] is None:
            raise "获取账户信息失败，请检查Mint地址和RPC节点"
        
        input_mint_token_program = input_info["result"]["value"]["owner"]
        output_mint_token_program = output_info["result"]["value"]["owner"]
        
        logger.info("Input Mint Token Program:", input_mint_token_program)
        logger.info("Output Mint Token Program:", output_mint_token_program)
        
        # 构造创建订单的请求数据
        payload = {
            "inputMint": input_mint_addr,
            "outputMint": output_mint_addr,
            "maker": swap_event.user_pubkey,
            "payer": swap_event.user_pubkey,
            "params": {
                "makingAmount": swap_event.amount,
                "takingAmount": swap_event.ui_amount*ratio,
                # "expiredAt": "",  # Unix时间戳（例如：int(time.time())），可选参数
                # "feeBps": "",     # 如有需要，指定交易手续费bps，可选参数
            },
            "computeUnitPrice": "auto",
            # "referral": "",  # 可选，如果指定则为 output mint 的推荐token账户
            "inputTokenProgram": input_mint_token_program,   # 默认使用token程序或指定其他（如token2022）
            "outputTokenProgram": output_mint_token_program,
            # "wrapAndUnwrapSol": True,  # 默认True或可选参数
        }
        
        headers = {
            "Content-Type": "application/json",
            # "x-api-key": ""  # 如有需要，在此填写API key
        }
        
        # 发送POST请求创建订单
        response = requests.post("https://api.jup.ag/limit/v2/createOrder", headers=headers, json=payload)
        if response.status_code != 200:
            raise f"请求创建订单失败，状态码：{response.status_code}, 响应：{response.text}"
        
        create_order_response = response.json()
        logger.info("Create Order Response:", create_order_response)
        
        # 获取返回的交易（Base64编码）并进行反序列化
        transaction_base64 = create_order_response["tx"]
        transaction_bytes = base64.b64decode(transaction_base64)
        transaction = VersionedTransaction(transaction_bytes)
        
        # 假设已定义钱包（Keypair），请替换为你的钱包私钥
        # 示例：wallet = Keypair.from_secret_key(<你的私钥字节数组>)
        wallet = Keypair()  # 这里只是示例，实际使用时请加载你的私钥
        
        # 使用钱包对交易进行签名
        transaction.signatures([wallet])
        
        # 序列化签名后的交易
        transaction_binary = transaction.serialize()
        
        # 发送原始交易
        send_response = self.rpc_client.send_raw_transaction(transaction_binary, opts={"skipPreflight": True, "max_retries": 2})
        signature = send_response["result"]
        logger.info("Transaction Signature:", signature)
        
        # 等待交易确认
        confirmation = self.rpc_client.confirm_transaction(signature, commitment="finalized")
        # 检查交易是否存在错误
        if confirmation["result"]["value"] is not None and confirmation["result"]["value"].get("err") is not None:
            raise f"Transaction failed: {json.dumps(confirmation['result']['value'].get('err'))}\n\nhttps://solscan.io/tx/{signature}/"
        else:
            logger.info(f"Transaction successful: https://solscan.io/tx/{signature}/")
        
    async def _record_failed_swap(self, swap_event: SwapEvent) -> SwapResult:
        """记录失败的交易结果"""
        swap_result = SwapResult(
            swap_event=swap_event,
            user_pubkey=swap_event.user_pubkey,
            transaction_hash=None,
            submmit_time=int(time.time()),
        )
        await self.swap_result_producer.produce(swap_result)
        return swap_result

    async def _process_swap_event(self, swap_event: SwapEvent):
        """创建新的任务来处理交易事件"""
        task = asyncio.create_task(self._process_single_swap_event(swap_event))
        self.task_pool.add(task)
        task.add_done_callback(self.task_pool.discard)

    async def start(self):
        processor_task = asyncio.create_task(self.copytrade_processor.start())
        # 添加任务完成回调以处理可能的异常
        processor_task.add_done_callback(lambda t: t.exception() if t.exception() else None)
        # 启动所有消费者
        for consumer in self.swap_event_consumers:
            await consumer.start()

    async def stop(self):
        """优雅关闭所有消费者"""
        # 停止跟单交易
        self.copytrade_processor.stop()

        # 停止所有消费者
        for consumer in self.swap_event_consumers:
            consumer.stop()

        if self.task_pool:
            logger.info("Waiting for remaining tasks to complete...")
            await asyncio.gather(*self.task_pool, return_exceptions=True)
        logger.info("All consumers stopped")


if __name__ == "__main__":
    pre_start()
    trading = Trading()
    try:
        asyncio.run(trading.start())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        asyncio.run(trading.stop())
        logger.info("Shutdown complete")
