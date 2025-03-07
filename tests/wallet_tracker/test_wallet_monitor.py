# import pytest
# from solders.pubkey import Pubkey
# from wallet_monitor.main import WalletMonitor, get_wallet_tokens
# from solbot_common.utils import get_async_client

# # 标记整个模块使用异步
# pytestmark = pytest.mark.asyncio

# async def test_get_wallet_tokens():
#     # 准备测试数据
#     wallet_address = Pubkey.from_string("BQWWFhzBnb1T4vD7SC8dS9qE1zrWWXe1LikeaAG5iuKm")
#     client = get_async_client()

#     # 执行测试
#     token_accounts = await get_wallet_tokens(wallet_address, client)

#     # 验证结果
#     assert isinstance(token_accounts, list)
#     if len(token_accounts) > 0:
#         for account in token_accounts:
#             assert hasattr(account, 'mint')
#             assert hasattr(account, 'owner')
#             assert hasattr(account, 'balance')
#             assert hasattr(account, 'decimals')
#             assert hasattr(account, 'state')

# async def test_wallet_monitor():
#     # 准备测试数据
#     wallets = [
#         Pubkey.from_string("BQWWFhzBnb1T4vD7SC8dS9qE1zrWWXe1LikeaAG5iuKm")
#     ]
#     monitor = WalletMonitor(wallets)

#     # 执行测试
#     await monitor.sync_wallet()

#     # 这里可以添加数据库验证
#     # with start_session() as session:
#     #     accounts = session.query(AssociatedTokenAccount).all()
#     #     assert len(accounts) > 0
