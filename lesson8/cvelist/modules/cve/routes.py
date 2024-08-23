from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import CveDTO, CreateCveSchema, UpdateCveSchema
from cvelist.deps import get_db_session
from cvelist.modules.cve import crud

cve_router = APIRouter(prefix="/cve")


@cve_router.post("/", response_model=CveDTO, status_code=201)
async def create_cve(
    body: CreateCveSchema, db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CveDTO:
    return await crud.create(db_session, body)


@cve_router.get("/", response_model=list[CveDTO])
async def get_list_cve(
    db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> list[CveDTO]:
    return await crud.get_list(db_session)


@cve_router.get("/{cve_id}", response_model=CveDTO)
async def get_cve(
    cve_id: str, db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CveDTO:
    return await crud.get_by_id(db_session, cve_id)


@cve_router.put("/{cve_id}", response_model=CveDTO)
async def update_cve(
    cve_id: str, body: UpdateCveSchema, db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CveDTO:
    return await crud.update(db_session, cve_id, body)


@cve_router.delete("/{cve_id}", status_code=204)
async def delete_cve(cve_id: str, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    return await crud.delete(db_session, cve_id)
