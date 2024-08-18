from typing import AsyncIterator

import aiofiles
import aiofiles.os


async def _get_years_dirs(source_dir: str) -> AsyncIterator[str]:
    entries_iterator = await aiofiles.os.scandir(source_dir)
    for entry in entries_iterator:
        if entry.is_dir():
            yield entry.path


async def _get_files_from_year_dir(source_dir: str) -> AsyncIterator[str]:
    entries_iterator = await aiofiles.os.scandir(source_dir)
    for entry in entries_iterator:
        if not entry.is_dir():
            continue

        for file_path in await aiofiles.os.scandir(entry.path):
            yield file_path.path


async def get_files(source_dir: str) -> AsyncIterator[str]:
    async for year_dir in _get_years_dirs(source_dir):
        async for file_path in _get_files_from_year_dir(year_dir):
            yield file_path
