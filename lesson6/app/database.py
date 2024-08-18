from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from .config import Config


def get_engine() -> AsyncEngine:
    return create_async_engine(Config.DB_URI)


def make_session_class(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, expire_on_commit=False)
