from common.log import logger
from common.sentry import init_sentry as _init_sentry
from db.session import init_db as _init_db


def pre_start(
    init_db: bool = True,
    init_sentry: bool = True,
):
    if init_db:
        _init_db()
        logger.info("Database initialized")

    if init_sentry:
        _init_sentry()
        logger.info("Sentry initialized")
