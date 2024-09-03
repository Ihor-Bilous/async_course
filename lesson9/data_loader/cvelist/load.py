import asyncio

from typing import AsyncIterator

from .config import settings
from .extractor import extractor_worker
from .loader import loader_worker, bulk_create, bulk_update, LoaderActions
from .monitoring import monitoring_worker

CALLBACK_FUNCTION = {
    LoaderActions.CREATE.value: bulk_create,
    LoaderActions.UPDATE.value: bulk_update,
}


async def load_cve(
    files: AsyncIterator[str],
    extractor_workers_number: int = settings.EXTRACTOR_WORKERS_NUMBER,
    loader_workers_number: int = settings.LOADER_WORKERS_NUMBER,
    fetching: bool = False
):
    monitoring_queue = asyncio.Queue()
    extractor_queue = asyncio.Queue(
        maxsize=extractor_workers_number * settings.QUEUE_MAX_SIZE_COEFFICIENT
    )

    loader_queues = {
        LoaderActions.CREATE.value: asyncio.Queue(
            maxsize=(
                loader_workers_number
                * settings.BULK_INSERT_BATCH_SIZE
                * settings.QUEUE_MAX_SIZE_COEFFICIENT
            )
        ),
    }
    if fetching:
        loader_queues[LoaderActions.UPDATE.value] = asyncio.Queue(
            maxsize=(
                loader_workers_number
                * settings.BULK_INSERT_BATCH_SIZE
                * settings.QUEUE_MAX_SIZE_COEFFICIENT
            )
        )

    extractor_workers = [
        asyncio.create_task(
            extractor_worker(
                worker_id=str(worker_id + 1),
                extractor_queue=extractor_queue,
                loader_queues=loader_queues
            )
        )
        for worker_id in range(extractor_workers_number)
    ]

    loader_workers = []
    for queue_type, loader_queue in loader_queues.items():
        loader_workers.extend([
            asyncio.create_task(
                loader_worker(
                    worker_id=f"{queue_type}-{str(worker_id + 1)}",
                    loader_queue=loader_queue,
                    loader_callback=CALLBACK_FUNCTION[queue_type],
                    monitoring_queue=monitoring_queue
                )
            )
            for worker_id in range(loader_workers_number)
        ])

    monitoring_task = asyncio.create_task(monitoring_worker(monitoring_queue))

    # Fill workers
    async for action, file_path in files:
        await extractor_queue.put((action, file_path))

    # Finish extractor workers
    for _ in range(extractor_workers_number):
        await extractor_queue.put(None)
    await extractor_queue.join()
    await asyncio.gather(*extractor_workers, return_exceptions=True)

    # Finish loader workers
    for loader_queue in loader_queues.values():
        for _ in range(loader_workers_number):
            await loader_queue.put(None)
        await loader_queue.join()
    await asyncio.gather(*loader_workers, return_exceptions=True)

    # Finish monitoring worker
    await monitoring_queue.put(None)
    await monitoring_queue.join()
    await monitoring_task
