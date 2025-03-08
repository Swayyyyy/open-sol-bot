import asyncio
import signal

from gmgnbot.Data import GMGN, OKLine
from solbot_common.log import logger
from solbot_common.prestart import pre_start
from solbot_common.config import settings

from solbot_db.redis import RedisClient
import time
import datetime
from gmgnbot.constants import NEW_TOKEN_QUEUE_KEY, NEW_TOKEN_CHANNEL

class GmgnMontior:
    def __init__(self,redis_client):
        self.tasks: set[asyncio.Task] = set()
        self._shutdown_event = asyncio.Event()
        self.gmgn_monitor = GMGN()
        self.OKLine = OKLine(settings.okline.channelAccessToken)
        self.redis = redis_client
        
    async def start(self):
        """启动监控服务"""
        logger.info("Starting pump monitor service...")
        await self.monitor_token()

        # 等待关闭信号
        await self._shutdown_event.wait()

    async def monitor_token(self):
        while True:
            try:
                new_token_info = self.gmgn_monitor.fetch_hot_token()
                tokens = new_token_info.loc[new_token_info['price_change_percent1h'] > 1000][['holder_count', 'address']]
                for i in tokens['address']:
                    result = await self.redis.sadd(NEW_TOKEN_QUEUE_KEY, i)
                    if result:
                        logger.info(f'add new token: {i}')
                        await self.add_to_delay_queue(NEW_TOKEN_CHANNEL, i, 600)
                        # await self.redis.lpush(NEW_TOKEN_CHANNEL, i)
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error processing item: {e}")
    
    async def add_to_delay_queue(self, queue_name, task_id, delay_seconds):
        score = int(time.time()) + delay_seconds
        await self.redis.zadd(queue_name, score, task_id)
        

async def main():
    pre_start()
    monitor = GmgnMontior()
    await monitor.init()
    await monitor.add_to_delay_queue(NEW_TOKEN_CHANNEL,'4AujdjhoadPob9h7qBrSkHyJ5FmA9kNE8MBqHAFufnCj', 5)
    
if __name__ == "__main__":
    asyncio.run(main())
