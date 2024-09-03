import asyncio


async def monitoring_worker(queue: asyncio.Queue):
    total = 0

    while True:
        objects_number = await queue.get()
        if objects_number is None:
            queue.task_done()
            break

        total += objects_number
        print("Monitoring: Objects loaded:", total)
        queue.task_done()

    print("Monitoring: Finished")
