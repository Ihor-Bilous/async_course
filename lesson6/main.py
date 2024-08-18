import asyncio
import argparse

from app.config import Config
from app.directory_parser import get_files
from app.loader import loader_worker
from app.extractor import extractor_worker
from app.monitoring import timer, monitoring_worker


parser = argparse.ArgumentParser()
parser.add_argument(
    "source_dir",
    type=str,
    help="Absolute path to the CVEs dir. For instance: /home/username/dev/cvelistV5/cves",
)


async def main():
    # get input arguments
    args = parser.parse_args()
    _source_directory = args.source_dir

    # Queues initialization
    extractor_queue = asyncio.Queue(
        maxsize=Config.EXTRACTOR_WORKERS_NUMBER * Config.QUEUE_MAX_SIZE_COEFFICIENT
    )
    loader_queue = asyncio.Queue(
        maxsize=(
            Config.LOADER_WORKERS_NUMBER
            * Config.BULK_INSERT_BATCH_SIZE
            * Config.QUEUE_MAX_SIZE_COEFFICIENT
        )
    )
    monitoring_queue = asyncio.Queue()

    # Workers initialization
    extractor_workers = [
        asyncio.create_task(extractor_worker(str(worker_id + 1), extractor_queue, loader_queue))
        for worker_id in range(Config.EXTRACTOR_WORKERS_NUMBER)
    ]
    loader_workers = [
        asyncio.create_task(loader_worker(loader_queue, monitoring_queue, str(worker_id + 1)))
        for worker_id in range(Config.LOADER_WORKERS_NUMBER)
    ]
    monitoring_task = asyncio.create_task(monitoring_worker(monitoring_queue))

    # Getting all files and passing them to extract queue
    # One of the improvement that I wanted to add but didn't find a short and a pretty
    # solution - it's disabling indexes before inserting and enabling in the end.
    # Only one way is deleting and creating indexes, but I don't really like this way.
    # In a production we can have two replicas of db (read, write).
    # Itt can speed up the whole process.
    async for file_path in get_files(args.source_dir):
        await extractor_queue.put(file_path)

    # Finish extractor workers
    for _ in range(Config.EXTRACTOR_WORKERS_NUMBER):
        await extractor_queue.put(None)

    await extractor_queue.join()
    await asyncio.gather(*extractor_workers, return_exceptions=True)

    # Finish loader workers
    for _ in range(Config.LOADER_WORKERS_NUMBER):
        await loader_queue.put(None)

    await loader_queue.join()
    await asyncio.gather(*loader_workers, return_exceptions=True)

    # Finish monitoring worker
    await monitoring_queue.put(None)
    await monitoring_queue.join()
    await monitoring_task


if __name__ == "__main__":
    with timer("Total time"):
        asyncio.run(main())
