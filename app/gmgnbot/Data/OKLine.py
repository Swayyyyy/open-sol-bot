import requests
from datetime import datetime
import pandas as pd

class OKLine:
    def __init__(self, apikey):
        self.headers = {
            'Ok-Access-Key': apikey
        }

    def get_sol_transaction(self, address, start_time, end_time):
        """获取Solana链上指定时间段内的代币转账记录
        
        Args:
            address (str): 钱包地址
            start_time (str): 开始时间,格式:'YYYY-MM-DD HH:MM:SS'
            end_time (str): 结束时间,格式:'YYYY-MM-DD HH:MM:SS'
            
        Returns:
            list: 转账记录列表
        """
        url = "https://www.oklink.com/api/v5/explorer/solana/token-transaction-list"
        
        # 转换时间格式为毫秒时间戳
        start_ts = int(datetime.strptime(start_time, 
                                       '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
        end_ts = int(datetime.strptime(end_time, 
                                     '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
        print(start_ts, end_ts)
        page = 1
        transactions = []
        
        while True:
            params = {
                'address': address,
                'limit': 100,
                'page': page,
                "protocolType": "sol"
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data['code'] != '0' or not data.get('data'):
                    break
                    
                # 获取交易列表
                tx_list = data['data'][0].get('transactionList', [])
                if not tx_list:
                    break
                    
                # 过滤指定时间段内的交易
                for tx in tx_list:
                    tx_time = int(tx.get('transactionTime', 0))
                    if start_ts <= tx_time <= end_ts:
                        transactions.append({
                            'txHash': tx.get('txId'),
                            'time': tx_time,
                            'from': tx.get('from'),
                            'to': tx.get('to'), 
                            'amount': tx.get('amount'),
                            'symbol': tx.get('token'),
                            'status': tx.get('state')
                        })
                    elif tx_time < start_ts:
                        return transactions
                
                if len(tx_list) < 100:
                    break
                    
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")
                break
                
        return pd.DataFrame(transactions)
    
#写个测试代码，获取指定地址的代币转账记录
if __name__ == "__main__":
    okline = OKLine("b514acd3-0a1a-4212-bf83-d5a356f92d1a")
    transactions = okline.get_sol_transaction("3A66ZaA2NJifJNnCH2JaSoxajJseh7VRUoBsZFH4k97o", "2025-02-05 00:00:00", "2025-02-09 00:00:00")
    print(transactions)