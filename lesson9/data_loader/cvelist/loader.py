import asyncio
from enum import Enum
from typing import Coroutine, Callable

import aiohttp

from .config import settings


class LoaderActions(Enum):
    CREATE = "create"
    UPDATE = "update"


async def bulk_create(cve_batch: list[dict]):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.CVE_LIST_API_BASE_URL}/api/cve",
            json=cve_batch
        ) as resp:
            if resp.status != 201:
                print(await resp.text())
                raise Exception("Loader: Something went wrong with API")


async def bulk_update(cve_batch: list[dict]):
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{settings.CVE_LIST_API_BASE_URL}/api/cve/bulk_update",
            json=cve_batch
        ) as resp:
            if resp.status != 200:
                print(await resp.text())
                raise Exception("Loader: Something went wrong with API")


async def loader_worker(
    worker_id: str,
    loader_queue: asyncio.Queue,
    loader_callback: Callable[[list[dict]], Coroutine],
    monitoring_queue: asyncio.Queue,
    batch_size: int = settings.BULK_INSERT_BATCH_SIZE
):
    print(f"Loader: worker #{worker_id} started")
    try:
        cve_batch = []
        while True:
            cve_dict = await loader_queue.get()

            if cve_dict is None:
                loader_queue.task_done()
                print(f"Loader: worker #{worker_id} is going to be closed")
                break

            cve_batch.append(cve_dict)

            if len(cve_batch) >= batch_size:
                await loader_callback(cve_batch)

                await monitoring_queue.put(len(cve_batch))

                cve_batch = []

            loader_queue.task_done()

        if cve_batch:
            print(f"Loader: worker #{worker_id} processing")
            await loader_callback(cve_batch)
            await monitoring_queue.put(len(cve_batch))

    except Exception as e:
        print(f"Loader: error in worker #{worker_id}: {e}")
        raise e

    print(f"Loader: worker #{worker_id} finished")
