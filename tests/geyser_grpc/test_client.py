import json

import base58
import pytest
from solbot_common.config import settings
from yellowstone_grpc.client import GeyserClient


class SolanaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base58.b58encode(obj).decode("utf-8")
        return super().default(obj)


@pytest.mark.asyncio
async def test_connect():
    geyser_client = await GeyserClient.connect(
        settings.rpc.geyser.endpoint, x_token=settings.rpc.geyser.api_key
    )
    await geyser_client.health_check()
