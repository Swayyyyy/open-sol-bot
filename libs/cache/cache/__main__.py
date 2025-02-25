from cache.main import main
import asyncio
from common.log import logger

try:
    asyncio.run(main())
except KeyboardInterrupt:
    logger.info("Received keyboard interrupt, shutting down...")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
