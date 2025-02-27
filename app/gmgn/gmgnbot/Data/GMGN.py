from gmgnbot.Data.CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions
from urllib.parse import urlencode
from common.log import logger
import pandas as pd
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time

from pyvirtualdisplay import Display
import atexit

arguments = [
    # "--remote-debugging-port=9222",  # Add this line for remote debugging
    "-no-first-run",
    "-force-color-profile=srgb",
    "-metrics-recording-only",
    "-password-store=basic",
    "-use-mock-keychain",
    "-export-tagged-pdf",
    "-no-default-browser-check",
    "-disable-background-mode",
    "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
    "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
    "-deny-permission-prompts",
    "-disable-gpu",
    "-accept-lang=en-US",
    #"-incognito" # You can add this line to open the browser in incognito mode by default 
]

class GMGN():
    def __init__(self, chrome_path="/usr/bin/google-chrome-stable"):
        print('Starting display')
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        print('Display started')
        
        def cleanup_display():
            if display:
                display.stop()
                
        atexit.register(cleanup_display)
        browser_path = chrome_path
        options = ChromiumOptions().auto_port()
        options.set_argument("--remote-debugging-port=15185")
        options.set_argument("--headless=new") 
        options.set_argument("--disable-gpu")  # Optional, helps in some cases
        options.set_argument("--no-sandbox")  # Optional, helps in some cases
        options.set_argument("--disable-dev-shm-usage") 
        
        options.set_paths(browser_path=browser_path).headless(False)
        
        self.driver = CloudflareBypasser(addr_or_opts=options)
        
    
    def fetch_trader_data(self, token_id, start_datetime, nums):
        """
        根据传入的 token_id、起始时间（datetime 对象）和记录条数，
        调用接口获取交易数据，并整理出所有的交易者信息为 pandas 的 DataFrame。

        参数：
        - token_id: 代币地址（字符串）
        - start_datetime: 起始时间，datetime 对象，例如 datetime(2025, 1, 1, 0, 0, 0)
        - limit: 从起始时间开始返回的记录条数

        返回：
        - 一个 pandas.DataFrame，包含接口返回的交易历史数据
        """
        # 将 datetime 对象转换为 Unix 时间戳（整数）
        start_timestamp = int(start_datetime.timestamp())
        
        # 构造基础 URL，将 token_id 填入 URL 中
        base_url = "https://gmgn.ai/api/v1/token_trades/sol/{}"
        base_url = base_url.format(token_id)
        trading_info = []
        for i in range(nums//100):
            logger.info(f"Fetching {i}th page of trading data for token {token_id}")
            # 构造请求参数
            params = {
                "tz_name": "Asia/Hong_Kong",
                "tz_offset": "28800",
                "app_lang": "en",
                "limit": 100,
                "maker": "",
                "from": start_timestamp,
                "revert": "true"
            }
            
            # 发送 GET 请求
            
            url = f"{base_url}?{urlencode(params)}"
            html = self.driver.request(url)
            html = BeautifulSoup(html, "html.parser")
            history = json.loads(html.text)["data"]["history"]
            if len(history) == 0:
                break
            # 将交易记录整理为 pandas DataFrame
            df = pd.DataFrame(history)
            start_timestamp = df['timestamp'].max()
            trading_info.append(df)
        df = pd.concat(trading_info)
        return df
    
    def fetch_kline_data(self, token_id, start_datetime, end_datetime, resolution="1m"):
        """
        根据传入的 token_id、开始时间和结束时间（均为 datetime 对象），
        获取历史 K 线数据，并整理为 pandas DataFrame。

        参数：
        - token_id: 代币地址（字符串）
        - start_datetime: 开始时间（datetime 对象）
        - end_datetime: 结束时间（datetime 对象）
        - resolution: 时间分辨率，默认为 "1m"（1分钟）
        
        返回：
        - 一个 pandas.DataFrame，包含 K 线数据（字段 open、close、high、low、time、volume）
        """
        # 将 datetime 对象转换为 Unix 时间戳（单位：秒）
        logger.info(f"Fetching Kline data for token {token_id}")
        start_ts = int(start_datetime.timestamp())
        end_ts = int(end_datetime.timestamp())
        
        # 构造基础 URL，将 token_id 填入 URL 中
        base_url = f"https://gmgn.ai/api/v1/token_kline/sol/{token_id}"
        
        # 构造请求参数
        params = {
            "tz_name": "Asia/Hong_Kong",
            "tz_offset": "28800",
            "app_lang": "en",
            "resolution": resolution,
            "from": start_ts,
            "to": end_ts
        }
        
        url = f"{base_url}?{urlencode(params)}"
        
        # 发起 GET 请求
        html = self.driver.request(url)
        html = BeautifulSoup(html, "html.parser")
        history = json.loads(html.text).get("data", {}).get("list", [])
        # 解析返回的 JSON 数据，并提取 K 线数据列表
        
        # 将数据整理为 pandas DataFrame
        df = pd.DataFrame(history)
        if resolution == "1m":
            time_delta = timedelta(minutes=1)
        elif resolution == "5m":
            time_delta = timedelta(minutes=5)
        elif resolution == "15m":
            time_delta = timedelta(minutes=15)
        elif resolution == "30m":
            time_delta = timedelta(minutes=30)
        elif resolution == "1h":
            time_delta = timedelta(hours=1)
        elif resolution == "4h":
            time_delta = timedelta(hours=4)
        elif resolution == "1d":
            time_delta = timedelta(days=1)
        else:
            time_delta = timedelta(minutes=1)
            
        # 将 time 字段（以毫秒为单位的时间戳）转换为 datetime 对象
        if not df.empty and "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"].astype(int), unit="ms")
        else:
            df["time"] = [start_datetime + i * time_delta for i in range(len(df))]
        
        return df

    def fetch_hot_token(self, interval="5m", min_created="1000m", max_created="1111111m"):
        """
        获取热门代币列表，返回前 limit 个代币的信息。

        参数：
        - limit: 返回的代币数量

        返回：
        - 一个 pandas.DataFrame，包含代币的信息（字段 id、name、symbol、price、change、volume）
        """
        # 构造 URL
        logger.info(f"Fetching hot token list")
        base_url = f"https://gmgn.ai/defi/quotation/v1/rank/sol/swaps/{interval}"
        data = {
            "device_id": "a3970227-1163-426a-b60b-3cc34832cf47",
            "client_id": "gmgn_web_2025.0210.151347",
            "from_app": "gmgn",
            "app_ver": "2025.0210.151347",
            "tz_name": "Asia/Shanghai",
            "tz_offset": "28800",
            "app_lang": "en",
            "orderby": "change1h",
            "direction": "desc",
            "min_created": min_created,
            "max_created": max_created
        }
        # 发起 GET 请求
        url = f"{base_url}?{urlencode(data)}"
        
        html = self.driver.request(url)
        html = BeautifulSoup(html, "html.parser")
        tokens = json.loads(html.text).get("data", {}).get('rank',[])
        
        # 将代币列表整理为 pandas DataFrame
        df = pd.DataFrame(tokens)
        return df
    
    def fetch_hoding(self, address):
        logger.info(f"Fetching hoding data for address {address}")
        base_url = f'https://gmgn.ai/api/v1/wallet_holdings/sol/{address}'
        data = {
            "tz_name": "Asia/Shanghai",
            "tz_offset": "28800",
            "app_lang": "en",
            "limit": 50,
            "orderby": "last_active_timestamp",
            "direction": "desc",
            "showsmall": "true",
            "sellout": "true",
            "hide_abnormal": "false"
        }
        url = f"{base_url}?{urlencode(data)}"
        # print(url)
        html = self.driver.request(url)
        html = BeautifulSoup(html, "html.parser")
        hoding = json.loads(html.text).get("data", {}).get('holdings',[])
        if hoding:
            for i in hoding:
                for k in i['token'].keys():
                    i[f'token_{k}'] = i['token'][k]
                i.pop('token')
        # 将代币列表整理为 pandas DataFrame
        df = pd.DataFrame(hoding)
        
        return df
        
        
if __name__ == "__main__":

    gmgn = GMGN()
    token_id = "BDW8YHasD3NSDjSHU9Xy6KXtshGayMGQfj5bJpLcpump"
    start_datetime = datetime(2025, 2, 1, 0, 0, 0)
    end_datetime = datetime(2025, 2, 2, 0, 0, 0)
    limit = 300
    df = gmgn.fetch_kline_data(token_id, start_datetime, end_datetime, "1m")
    print(df)
    df = gmgn.fetch_trader_data(token_id, start_datetime, limit)
    print(df)
    df = gmgn.fetch_hot_token()
    print(df)
    df = gmgn.fetch_hoding("HrpVCcF7ibkNLgZmTHgVnto4U7d4EbXFKD6bSJkko7jj")
    print(df)