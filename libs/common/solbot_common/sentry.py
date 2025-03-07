import sentry_sdk
from pydantic import HttpUrl, ValidationError

from solbot_common.config import settings


def init_sentry() -> None:
    if settings.sentry.enable is False:
        return

    dsn = settings.sentry.dsn
    try:
        HttpUrl(dsn)
    except ValidationError:
        raise ValueError("Invalid Sentry DSN, must be a valid URL")
    traces_sample_rate = settings.sentry.traces_sample_rate
    sentry_sdk.init(dsn=dsn, traces_sample_rate=traces_sample_rate)
