from solbot_db.session import init_db as _init_db

from solbot_common.log import logger
from solbot_common.sentry import init_sentry as _init_sentry


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
