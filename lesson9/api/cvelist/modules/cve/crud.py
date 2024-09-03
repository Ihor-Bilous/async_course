from datetime import datetime
from itertools import batched

from sqlalchemy import select, or_, func, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from cvelist.base.pagination import convert_pages_to_limits
from cvelist.config import settings
from cvelist.exceptions import ResourceDoesNotExist
from cvelist.orm.models import Cve
from cvelist.modules.cve.schemas import CveDTO, CreateCveSchema, UpdateCveSchema, CveListQuery


FROM = "_from"
TO = "_to"
DATE_RANGE_OPERATORS = {
    FROM: lambda field, value: (field >= value),
    TO: lambda field, value: (field <= value),
}


async def _get_by_id(db_session: AsyncSession, id: str) -> Cve:
    stmt = select(Cve).where(Cve.id == id)
    result = await db_session.execute(stmt)

    cve = result.scalar_one_or_none()
    if not cve:
        raise ResourceDoesNotExist
    return cve


def _generate_cve_date_range_filters(
    reserved_date_from: datetime | None = None,
    published_date_from: datetime | None = None,
    updated_date_from: datetime | None = None,
    reserved_date_to: datetime | None = None,
    published_date_to: datetime | None = None,
    updated_date_to: datetime | None = None,
):
    def get_field_and_operator(arg_name):
        if FROM in arg_name:
            return arg_name.split(FROM)[0], DATE_RANGE_OPERATORS[FROM]
        elif TO in arg_name:
            return arg_name.split(TO)[0], DATE_RANGE_OPERATORS[TO]
        return None, None

    arguments = locals()
    conditions = []

    for arg, value in arguments.items():
        if not value:
            continue

        field_name, filter_func = get_field_and_operator(arg)

        if field_name and filter_func:
            field = getattr(Cve, field_name)
            conditions.append(filter_func(field, value))

    return conditions


def _generate_cve_search_filters(search_string: str) -> list:
    return [
        func.lower(Cve.description).like(func.text(f'%{search_string.lower()}%')),
        func.lower(Cve.title).like(func.text(f'%{search_string.lower()}%')),
        func.lower(Cve.problem_types).like(func.text(f'%{search_string.lower()}%'))
    ]


async def bulk_create(
    db_session: AsyncSession,
    body: list[CreateCveSchema],
    batch_size: int = settings.BULK_CREATE_BATCH_SIZE,
) -> None:
    for batch in batched(body, batch_size):
        cve_items = [
            Cve(
                id=item.id,
                title=item.title,
                description=item.description,
                problem_types=item.problem_types,
                published_date=item.published_date,
                reserved_date=item.reserved_date,
                updated_date=item.updated_date,
            )
            for item in batch
        ]
        db_session.add_all(cve_items)
        await db_session.commit()


async def bulk_update(
    db_session: AsyncSession,
    body: list[UpdateCveSchema],
) -> None:
    """
    Unfortunately there is no in async version of sqlalchemy bulk_update_mappings method.
    Also, looks like asyncpg doesn't support executing several update statements splitter by semicolon
    at once. That's why I have next implementation of bulk update.
    """
    for item in body:
        cve_updates = item.model_dump()
        cve_id = cve_updates.pop("id")
        stmt = (
            update(Cve)
            .where(Cve.id == cve_id)
            .values(cve_updates)
        )
        await db_session.execute(stmt)
    await db_session.commit()


async def get_list(db_session: AsyncSession, query_params: CveListQuery) -> list[CveDTO]:
    limit, offset = convert_pages_to_limits(query_params.page, query_params.page_size)
    stmt = select(Cve)

    date_range_filters = _generate_cve_date_range_filters(
        query_params.reserved_date_from,
        query_params.published_date_from,
        query_params.updated_date_from,
        query_params.reserved_date_to,
        query_params.published_date_to,
        query_params.updated_date_to,
    )

    for condition in date_range_filters:
        stmt = stmt.where(condition)

    if query_params.search:
        stmt = stmt.where(or_(*_generate_cve_search_filters(query_params.search))).distinct(Cve.id)

    stmt = stmt.order_by(Cve.id.desc()).limit(limit).offset(offset)
    result = await db_session.execute(stmt)
    cve_items = result.scalars()
    return [CveDTO.model_validate(cve_orm) for cve_orm in cve_items]


async def get_by_id(db_session: AsyncSession, id: str) -> CveDTO:
    cve_orm = await _get_by_id(db_session, id)
    return CveDTO.model_validate(cve_orm)
