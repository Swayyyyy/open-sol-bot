from typing import Literal

from aiocache import Cache, caches
from aiocache import cached as _cached
from aiocache.base import SENTINEL
from solbot_common.config import settings

endpoint = settings.db.redis.host
port = settings.db.redis.port
# cache = Cache(cache_class=Cache.REDIS, endpoint=endpoint, port=port, namespace="cache")


# You can use either classes or strings for referencing classes
caches.set_config(
    {
        "temp": {
            "cache": "aiocache.SimpleMemoryCache",
            "serializer": {"class": "aiocache.serializers.StringSerializer"},
        },
        "default": {
            "cache": "aiocache.RedisCache",
            "endpoint": endpoint,
            "port": port,
            "timeout": 1,
            "serializer": {"class": "aiocache.serializers.PickleSerializer"},
            "plugins": [
                {"class": "aiocache.plugins.HitMissRatioPlugin"},
                {"class": "aiocache.plugins.TimingPlugin"},
            ],
            "namespace": "cache",
        },
    }
)


def key_builder(f, *args, **kwargs):
    # 获取 f 所在的模块名
    module_name = f.__module__
    # 获取 f 所在的文件名
    # file_name = f.__code__.co_filename
    # # 获取 f 所在的行号
    # line_number = f.__code__.co_firstlineno
    # # 获取 f 所在的函数名
    # function_name = f.__name__
    # 获取 f 所在的类名
    class_name = f.__qualname__.split(".")[0]
    try:
        # 获取 f 所在的方法名
        method_name = f.__qualname__.split(".")[1]
    except IndexError:
        # 如果是函数，则获取函数名
        method_name = f.__name__

    # 获取 f 所在的函数参数, 如果是实例方法，则不包含 self
    # if inspect.ismethod(f):
    #     args = args[1:]
    # elif inspect.iscoroutine(f):
    #     args = args[1:]

    args_str = ",".join(map(str, args))
    kwargs_str = ",".join(f"{k}={v}" for k, v in kwargs.items())
    return f"{module_name}:{class_name}:{method_name}:{args_str}:{kwargs_str}"


class cached(_cached):
    def __init__(
        self,
        ttl=SENTINEL,
        key=None,
        namespace=None,
        key_builder=key_builder,
        skip_cache_func=lambda x: False,
        cache=Cache.REDIS,
        serializer=None,
        plugins=None,
        alias: Literal["default", "temp"] = "default",
        noself=False,
        **kwargs,
    ):
        self.ttl = ttl
        self.key = key
        self.key_builder = key_builder
        self.skip_cache_func = skip_cache_func
        self.noself = noself
        self.alias = alias
        self.cache = None

        self._cache = cache
        self._serializer = serializer
        self._namespace = namespace
        self._plugins = plugins
        self._kwargs = kwargs
