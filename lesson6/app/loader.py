import asyncio

from .config import Config
from .database import get_engine, make_session_class
from .dtos import CveDTO
from .models import Cve

from sqlalchemy.ext.asyncio import AsyncEngine


def from_cve_dto_to_model(cve_dto: CveDTO) -> Cve:
    return Cve(
        cve_id=cve_dto.cve_id,
        title=cve_dto.title,
        description=cve_dto.description,
        problem_types=cve_dto.problem_types,
        reserved_date=cve_dto.reserved_date,
        published_date=cve_dto.published_date,
        updated_date=cve_dto.updated_date,
    )


async def bulk_insert(engine: AsyncEngine, cve_batch: list[Cve]) -> None:
    _Session = make_session_class(engine)
    async with _Session() as session:
        session.add_all(cve_batch)
        await session.flush(objects=cve_batch)
        await session.commit()


async def loader_worker(
    loader_queue: asyncio.Queue, monitoring_queue: asyncio.Queue, worker_id: str
):
    print(f"Loader worker #{worker_id} started")
    try:
        engine = get_engine()

        cve_batch = []
        while True:
            cve_dto = await loader_queue.get()

            if cve_dto is None:
                loader_queue.task_done()
                print(f"Loader worker #{worker_id} is going to be closed")
                break

            cve = from_cve_dto_to_model(cve_dto)
            cve_batch.append(cve)

            if len(cve_batch) >= Config.BULK_INSERT_BATCH_SIZE:
                await bulk_insert(engine, cve_batch)

                await monitoring_queue.put(len(cve_batch))
                cve_batch = []

            loader_queue.task_done()

        if cve_batch:
            print(f"Loader worker #{worker_id} processing")
            await bulk_insert(engine, cve_batch)
            await monitoring_queue.put(len(cve_batch))
    except Exception as e:
        print(f"Error in Loader worker #{worker_id}: {e}")
        raise e

    print(f"Loader worker #{worker_id} finished")
