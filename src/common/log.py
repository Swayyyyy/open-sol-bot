import sys
from pathlib import Path
from loguru import logger
from common.config import settings

__all__ = ["logger"]

LOG_LEVEL = settings.log.level.upper()
logger.configure(handlers=[{"sink": sys.stderr, "level": LOG_LEVEL}])

# Remove default handler
logger.remove()

# Add console handler with custom format
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
    enqueue=True,
)

# Add file handler for errors
log_path = Path(__file__).parent.parent.parent / "logs"
log_path.mkdir(exist_ok=True)
logger.add(
    log_path / "error.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="1 day",
    retention="7 days",
    enqueue=True,
)
