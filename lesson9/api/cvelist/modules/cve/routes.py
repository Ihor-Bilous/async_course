from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cvelist.deps import get_db_session
from cvelist.modules.cve import crud
from cvelist.modules.cve.schemas import CveDTO, CreateCveSchema, UpdateCveSchema, CveListQuery

cve_router = APIRouter(prefix="/cve")


@cve_router.post("/", status_code=201)
async def create_cves(
    body: list[CreateCveSchema], db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> None:
    return await crud.bulk_create(db_session, body)


@cve_router.get("/", response_model=list[CveDTO])
async def get_list_cve(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    query: CveListQuery = Depends(),
) -> list[CveDTO]:
    return await crud.get_list(db_session, query)


@cve_router.get("/{cve_id}", response_model=CveDTO)
async def get_cve(
    cve_id: str, db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CveDTO:
    return await crud.get_by_id(db_session, cve_id)


@cve_router.put("/bulk_update")
async def update_cves(
    body: list[UpdateCveSchema], db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> None:
    return await crud.bulk_update(db_session, body)
