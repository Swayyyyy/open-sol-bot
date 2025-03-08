from solana.rpc.async_api import AsyncClient
from solbot_cache.token_info import TokenInfoCache
from solbot_common.constants import SOL_DECIMAL, WSOL
from solbot_common.utils.jupiter import JupiterAPI
from solders.keypair import Keypair  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore

from trading.swap import SwapDirection, SwapInType
from trading.tx import sign_transaction_from_raw

from .base import TransactionBuilder


class JupiterLimitTransactionBuilder(TransactionBuilder):
    """Jupiter 交易构建器"""

    def __init__(self, rpc_client: AsyncClient) -> None:
        super().__init__(rpc_client=rpc_client)
        self.token_info_cache = TokenInfoCache()
        self.jupiter_client = JupiterAPI()

    #TODO 修改为限价订单
    async def build_swap_transaction(
        self,
        keypair: Keypair,
        token_address: str,
        ui_amount: float,
        swap_direction: SwapDirection,
        slippage_bps: int,
        in_type: SwapInType | None = None,
        use_jito: bool = False,
        priority_fee: float | None = None,
    ) -> VersionedTransaction:
        """Build swap transaction with GMGN API.

        Args:
            token_address (str): token address
            amount_in (float): amount in
            swap_direction (SwapDirection): swap direction
            slippage (int): slippage, percentage
            in_type (SwapInType | None, optional): in type. Defaults to None.
            use_jto (bool, optional): use jto. Defaults to False.
            priority_fee (float | None, optional): priority fee. Defaults to None.

        Returns:
            VersionedTransaction: The built transaction ready to be signed and sent
        """
        if swap_direction == "sell" and in_type is None:
            raise ValueError("in_type must be specified when selling")

        if swap_direction == SwapDirection.Buy:
            token_in = str(WSOL)
            token_out = token_address
            amount = int(ui_amount * SOL_DECIMAL)
        elif swap_direction == SwapDirection.Sell:
            token_info = await self.token_info_cache.get(token_address)
            if token_info is None:
                raise ValueError("Token info not found")
            decimals = token_info.decimals
            token_in = token_address
            token_out = str(WSOL)
            amount = int(ui_amount * 10**decimals)
        else:
            raise ValueError("swap_direction must be buy or sell")

        if use_jito and priority_fee is None:
            raise ValueError("priority_fee must be specified when using jito")

        swap_tx_response = await self.jupiter_client.get_swap_transaction(
            input_mint=token_in,
            output_mint=token_out,
            user_publickey=str(keypair.pubkey()),
            amount=amount,
            slippage_bps=slippage_bps,
            use_jito=use_jito,
            jito_tip_lamports=int(priority_fee * SOL_DECIMAL) if priority_fee else None,
        )
        swap_tx = swap_tx_response["swapTransaction"]
        signed_tx = await sign_transaction_from_raw(swap_tx, keypair)
        return signed_tx

    
    
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