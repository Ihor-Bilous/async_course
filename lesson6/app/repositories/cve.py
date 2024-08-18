from typing import AsyncIterator

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Cve


async def get_by_id(session: AsyncSession, id_: str):
    stmt = select(Cve).where(Cve.id == id_).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_by_cve_id(session: AsyncSession, cve_id: str):
    stmt = select(Cve).where(Cve.cve_id == cve_id).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one()


async def filter_(
    session: AsyncSession,
    filters: list,
    limit: int = 50,
    offset: int = 0,
) -> AsyncIterator[Cve]:
    stmt = select(Cve).where(*filters).order_by(Cve.published_date).limit(limit).offset(offset)
    result = await session.stream(stmt)

    async for row in result.scalars():
        yield row
