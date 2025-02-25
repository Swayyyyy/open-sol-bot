import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Optional, Tuple

import grpc
from grpc.aio._channel import Channel
from grpc_health.v1 import health_pb2, health_pb2_grpc

from .grpc import geyser_pb2, geyser_pb2_grpc
from .types import CommitmentLevel


@dataclass
class InterceptorXToken(
    grpc.aio.UnaryUnaryClientInterceptor,
    grpc.aio.UnaryStreamClientInterceptor,
    grpc.aio.StreamUnaryClientInterceptor,
    grpc.aio.StreamStreamClientInterceptor,
):
    x_token: Optional[str] = None
    x_request_snapshot: bool = False

    def _inject_token(self, client_call_details):
        if self.x_token:
            metadata = []
            if client_call_details.metadata is not None:
                metadata = list(client_call_details.metadata)
            metadata.append(("x-token", self.x_token))
            if self.x_request_snapshot:
                metadata.append(("x-request-snapshot", "true"))
            return client_call_details._replace(metadata=metadata)
        return client_call_details

    async def intercept_unary_unary(
        self,
        continuation,
        client_call_details,
        request,
    ):
        new_details = self._inject_token(client_call_details)
        return await continuation(new_details, request)

    async def intercept_unary_stream(
        self,
        continuation,
        client_call_details,
        request,
    ):
        new_details = self._inject_token(client_call_details)
        return continuation(new_details, request)

    async def intercept_stream_unary(
        self,
        continuation,
        client_call_details,
        request_iterator,
    ):
        new_details = self._inject_token(client_call_details)
        return await continuation(new_details, request_iterator)

    async def intercept_stream_stream(
        self,
        continuation,
        client_call_details,
        request_iterator,
    ):
        new_details = self._inject_token(client_call_details)
        return continuation(new_details, request_iterator)


class GeyserClient:
    def __init__(self, channel: Channel):
        self._channel = channel
        self.health = health_pb2_grpc.HealthStub(channel)
        self.geyser = geyser_pb2_grpc.GeyserStub(channel)

    @classmethod
    async def connect(
        cls,
        endpoint: str,
        x_token: Optional[str] = None,
        x_request_snapshot: bool = False,
        **kwargs,
    ) -> "GeyserClient":
        interceptor = InterceptorXToken(
            x_token=x_token, x_request_snapshot=x_request_snapshot
        )
        if "interceptors" in kwargs:
            kwargs["interceptors"].append(interceptor)
        else:
            kwargs["interceptors"] = [interceptor]

        credentials = grpc.ssl_channel_credentials()
        channel = grpc.aio.secure_channel(endpoint, credentials, **kwargs)
        return cls(channel)

    async def close(self):
        await self._channel.close()

    async def health_check(self) -> health_pb2.HealthCheckResponse:
        request = health_pb2.HealthCheckRequest(service="geyser.Geyser")
        return await self.health.Check(request)

    async def health_watch(
        self,
    ) -> AsyncGenerator[health_pb2.HealthCheckResponse, None]:
        request = health_pb2.HealthCheckRequest(service="geyser.Geyser")
        async for response in self.health.Watch(request):
            yield response

    async def subscribe(
        self,
    ) -> Tuple[
        asyncio.Queue[geyser_pb2.SubscribeRequest],
        AsyncGenerator[geyser_pb2.SubscribeUpdate, None],
    ]:
        return await self.subscribe_with_request(None)

    async def subscribe_with_request(
        self,
        request: Optional[geyser_pb2.SubscribeRequest] = None,
    ) -> Tuple[
        asyncio.Queue[geyser_pb2.SubscribeRequest],
        AsyncGenerator[geyser_pb2.SubscribeUpdate, None],
    ]:
        request_queue = asyncio.Queue()

        if request:
            await request_queue.put(request)

        async def request_iterator():
            while True:
                try:
                    yield await request_queue.get()
                except asyncio.CancelledError:
                    break

        call = self.geyser.Subscribe(request_iterator())

        async def response_generator():
            async for response in call:
                yield response

        return request_queue, response_generator()

    async def ping(self, count: int) -> geyser_pb2.PongResponse:
        request = geyser_pb2.PingRequest(count=count)
        return await self.geyser.Ping(request)

    async def get_latest_blockhash(
        self, commitment: Optional[CommitmentLevel] = None
    ) -> geyser_pb2.GetLatestBlockhashResponse:
        request = geyser_pb2.GetLatestBlockhashRequest()
        if commitment is not None:
            request.commitment = commitment.value
        proto_response = await self.geyser.GetLatestBlockhash(request)
        return geyser_pb2.GetLatestBlockhashResponse(
            slot=proto_response.slot,
            blockhash=proto_response.blockhash,
            last_valid_block_height=proto_response.last_valid_block_height,
        )

    async def get_block_height(
        self, commitment: Optional[CommitmentLevel] = None
    ) -> geyser_pb2.GetBlockHeightResponse:
        request = geyser_pb2.GetBlockHeightRequest()
        if commitment is not None:
            request.commitment = commitment.value
        proto_response = await self.geyser.GetBlockHeight(request)
        return geyser_pb2.GetBlockHeightResponse(
            block_height=proto_response.block_height
        )

    async def get_slot(
        self, commitment: Optional[CommitmentLevel] = None
    ) -> geyser_pb2.GetSlotResponse:
        request = geyser_pb2.GetSlotRequest()
        if commitment is not None:
            request.commitment = commitment.value
        proto_response = await self.geyser.GetSlot(request)
        return geyser_pb2.GetSlotResponse(slot=proto_response.slot)

    async def is_blockhash_valid(
        self, blockhash: str, commitment: Optional[CommitmentLevel] = None
    ) -> geyser_pb2.IsBlockhashValidResponse:
        request = geyser_pb2.IsBlockhashValidRequest(blockhash=blockhash)
        if commitment is not None:
            request.commitment = commitment.value
        proto_response = await self.geyser.IsBlockhashValid(request)
        return geyser_pb2.IsBlockhashValidResponse(
            slot=proto_response.slot,
            valid=proto_response.valid,
        )

    async def get_version(self) -> geyser_pb2.GetVersionResponse:
        request = geyser_pb2.GetVersionRequest()
        proto_response = await self.geyser.GetVersion(request)
        return geyser_pb2.GetVersionResponse(version=proto_response.version)
