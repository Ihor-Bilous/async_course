import argparse
import asyncio
import os
import re

from pathlib import Path
from typing import AsyncIterator

import aiohttp
import aiofiles

FETCH_PAGE_TIMEOUT = os.getenv("FETCH_PAGE_TIMEOUT", 2)
OUTPUT_DIR = "data/output/"

parser = argparse.ArgumentParser(description="Script for fetching web pages data.")
parser.add_argument(
    "filepath",
    type=str,
    help=(
        "Absolute path to text file with resources. "
        "For instance: /home/user/dev/async_fetcher/resources.txt"
    )
)


"""
Code in current comment I used to see how to work with AsyncContextManager.
It can be really useful when we have additional logic before/after writing
and it can be encapsulated in AsyncFileWriter.
---------------------------------------------------------------------------

from typing import Self


class AsyncFileWriter:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._file = None

    async def __aenter__(self) -> Self:
        self._file = await aiofiles.open(self.file_path, "wb")
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._file.close()
        if exc_type:
            raise exc_type(exc).with_traceback(tb)

    async def write(self, data) -> None:
        # do_something()
        await self._file.write(data)
        # do_something()


async def process_url(session: aiohttp.ClientSession, url: str) -> None:
    output_file_path = f"{OUTPUT_DIR}/{uuid.uuid4()}.html"
    async with AsyncFileWriter(output_file_path) as writer:
        async for chunk in fetch_page_chunks(session, url):
            await writer.write(chunk)
"""


def compute_file_name_from_url(url) -> str:
    result = re.sub(r"[^\w.]", "_", url)
    return result.strip("_")


async def read_lines(file_path: str | Path) -> AsyncIterator[str]:
    async with aiofiles.open(file_path, "r") as file_:
        async for line in file_:
            yield line


async def fetch_page(session: aiohttp.ClientSession, url: str) -> bytes:
    """
    This function can be a sync generator. The script will become a little bit slower
    but loading by chunks doesn't load the whole page content into memory, and it can be
    a good approach in saving memory. Unfortunately, I reverted this changes because it's hard
    to handle timeout. I found the way how to do it, but file will be created not fully in this
    case. Then removing of the file should be implemented. I think big pages will be handled by
    timeout and won't be loaded into memory.

    async def fetch_page_chunks(
        session: aiohttp.ClientSession, url: str, chunk_size: int = DEFAULT_CHUNK_SIZE
    ) -> AsyncIterator[bytes]:
        async with session.get(url) as response:
        try:
            async with asyncio.timeout(0.05):
                async for chunk in response.content.iter_chunked(chunk_size):
                    print(type(chunk))
                    yield chunk
        except TimeoutError:
            print("Timed out waiting for")
    """
    async with session.get(url) as response:
        # I'm reading bytes, not str, because it's less memory consuming
        return await response.read()


async def write_file(file_path: str | Path, page_content: bytes) -> None:
    async with aiofiles.open(file_path, "wb") as file_:
        await file_.write(page_content)


async def process_url(session: aiohttp.ClientSession, url: str) -> None:
    output_file_path = Path(OUTPUT_DIR, f"{compute_file_name_from_url(url)}.html")

    try:
        async with asyncio.timeout(FETCH_PAGE_TIMEOUT):
            page_content = await fetch_page(session, url)
    except TimeoutError:
        print(f"The long operation timed out. Page {url} is not loaded.")
    else:
        await write_file(output_file_path, page_content)


async def main():
    args = parser.parse_args()

    tasks = []

    async with aiohttp.ClientSession() as session:
        async for line in read_lines(args.filepath):
            url = line.strip()
            task = asyncio.create_task(process_url(session, url))
            tasks.append(task)

        await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.run(main())
