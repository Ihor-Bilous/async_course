import asyncio
import time
from contextlib import contextmanager


@contextmanager
def timer(msg: str):
    start = time.perf_counter()
    yield
    print(f"{msg}: {time.perf_counter() - start:.2f} seconds")


async def monitoring_worker(queue: asyncio.Queue):
    total = 0

    while True:
        objects_number = await queue.get()
        if objects_number is None:
            queue.task_done()
            break

        total += objects_number
        print("Objects loaded:", total)
        queue.task_done()

    print("Monitoring finished")
