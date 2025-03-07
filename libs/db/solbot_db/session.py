import contextlib
import functools
from collections.abc import AsyncGenerator, Generator
from inspect import iscoroutinefunction
from typing import ParamSpec, TypedDict, TypeVar, cast
from urllib.parse import urlparse

from solbot_common.config import settings
from solbot_common.log import logger
from solbot_common.models import *
from sqlalchemy import Engine, exc, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import Session, SQLModel, create_engine

# 创建全局引擎实例
engine = create_engine(
    settings.db.mysql_url,
    pool_size=5,  # 连接池大小
    max_overflow=10,  # 超过 pool_size 后最多可以创建的连接数
    pool_timeout=30,  # 等待连接的超时时间
    pool_recycle=1800,  # 连接重置时间，避免连接被数据库断开
)
# SessionBulder = sessionmaker(bind=engine)

# 创建异步引擎实例
async_engine = create_async_engine(
    settings.db.async_mysql_url,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)
AsyncSessionBuiler = async_sessionmaker(bind=async_engine)


def _create_database_if_not_exists(url: str):
    """创建数据库如果不存在"""
    parsed = urlparse(url)
    database = parsed.path.lstrip("/")

    # 创建一个没有指定数据库的连接URL
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    engine = create_engine(base_url, isolation_level="AUTOCOMMIT")

    try:
        # 检查数据库是否存在
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database}'"
                )
            )
            database_exists = result.scalar() is not None

            if not database_exists:
                logger.info(f"Creating database {database}")
                conn.execute(text(f"CREATE DATABASE {database}"))
                logger.info(f"Database {database} created successfully")
            else:
                logger.info(f"Database {database} already exists")
    except exc.SQLAlchemyError as e:
        logger.error(f"Error checking/creating database: {e}")
        raise
    finally:
        engine.dispose()


def create_db_and_tables(engine: Engine):
    """创建所有表"""
    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def init_db():
    """初始化数据库和表"""
    _create_database_if_not_exists(settings.db.mysql_url)

    # 创建表
    create_db_and_tables(engine)
    engine.dispose()


@contextlib.contextmanager
def start_session() -> Generator[Session, None, None]:
    """获取数据库会话的上下文管理器"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        try:
            session.rollback()
        except exc.PendingRollbackError:
            pass
    finally:
        session.close()


@contextlib.asynccontextmanager
async def start_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话的上下文管理器"""
    session = AsyncSessionBuiler()
    try:
        yield session
        await session.commit()
    except Exception as e:
        try:
            await session.rollback()
        except exc.PendingRollbackError:
            pass
        raise e
    finally:
        await session.close()


NEW_SESSION = cast(Session, None)
NEW_ASYNC_SESSION = cast(AsyncSession, None)
DBSession = Session | AsyncSession


class KwargsWithSession(TypedDict):
    session: DBSession


P = ParamSpec("P")
R = TypeVar("R", KwargsWithSession, dict)


def provide_session(func):
    """会话装饰器，根据被装饰函数是同步还是异步，提供相应的数据库会话

    如果函数已经有session参数，则直接使用该session，否则创建新的session
    """
    if iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs):
            if "session" not in kwargs:
                async with start_async_session() as session:
                    return await func(*args, session=session, **kwargs)
            else:
                return await func(*args, **kwargs)

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if "session" not in kwargs:
                with start_session() as session:
                    return func(*args, session=session, **kwargs)
            else:
                return func(*args, **kwargs)

        return sync_wrapper
