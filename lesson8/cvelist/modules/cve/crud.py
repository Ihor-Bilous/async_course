from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cvelist.exceptions import ResourceDoesNotExist
from cvelist.orm.models import Cve
from cvelist.modules.cve.schemas import CveDTO, CreateCveSchema, UpdateCveSchema


async def _get_by_id(db_session: AsyncSession, pk: str) -> Cve:
    stmt = select(Cve).where(Cve.id == pk)
    result = await db_session.execute(stmt)

    cve = result.scalar_one_or_none()
    if not cve:
        raise ResourceDoesNotExist
    return cve


async def create(db_session: AsyncSession, body: CreateCveSchema) -> CveDTO:
    current_year = datetime.now().year
    cve_id = await Cve.generate_id(db_session, current_year)
    cve = Cve(
        id=cve_id,
        title=body.title,
        description=body.description,
        problem_types=body.problem_types,
        published_date=datetime.now(),
    )
    db_session.add(cve)
    await db_session.flush()
    await db_session.commit()
    return CveDTO.from_model_to_dto(cve)


async def get_list(db_session: AsyncSession) -> list[CveDTO]:
    stmt = select(Cve).order_by(Cve.id.desc())
    result = await db_session.execute(stmt)
    cve_items = result.scalars()
    return [CveDTO.from_model_to_dto(cve) for cve in cve_items]


async def get_by_id(db_session: AsyncSession, pk: str) -> CveDTO:
    cve = await _get_by_id(db_session, pk)
    return CveDTO.from_model_to_dto(cve)


async def update(db_session: AsyncSession, pk: str, body: UpdateCveSchema) -> CveDTO:
    cve = await _get_by_id(db_session, pk)

    cve.updated_date = datetime.now()
    for key, value in body.model_dump().items():
        setattr(cve, key, value)

    db_session.add(cve)
    await db_session.flush()
    await db_session.commit()

    return CveDTO.from_model_to_dto(cve)


async def delete(db_session: AsyncSession, pk: str) -> None:
    cve = await _get_by_id(db_session, pk)
    await db_session.delete(cve)
    await db_session.flush()
    await db_session.commit()
