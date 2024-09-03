from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncSession:
    _Session = request.app.async_session_cls
    async with _Session() as session:
        yield session
