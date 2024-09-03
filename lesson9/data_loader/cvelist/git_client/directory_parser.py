import json
from datetime import datetime
from typing import AsyncIterator

import aiofiles
import aiofiles.os

from cvelist.utils import date_parser


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
    """Get all json files path from cvelist repo"""
    async for year_dir in _get_years_dirs(source_dir):
        async for file_path in _get_files_from_year_dir(year_dir):
            yield "create", file_path


async def _get_cve_changes_logs(file_path: str) -> AsyncIterator[dict]:
    """
    This function allows read big json files in generative way by one item.
    This is not genetic and works with structure from deltaLog.json file
    """
    async with aiofiles.open(file_path, 'r') as file:
        # skipping first line
        await anext(file)

        buffer = ""
        async for line in file:
            buffer += line
            try:
                buffer_copy = buffer[:]
                buffer_copy = buffer_copy.replace("\n", "").rstrip(",")
                json_item = json.loads(buffer_copy)
            except json.decoder.JSONDecodeError:
                continue
            yield json_item
            buffer = ""


def _generate_file_paths(source_dir: str, obj_list: dict):
    result = []
    for obj in obj_list:
        try:
            relative_file_path = obj["githubLink"].split("cves")[1]
            result.append(f"{source_dir}/{relative_file_path}")
        except (KeyError, IndexError):
            continue
    return result


async def get_new_fetched_files(source_dir: str, last_fetching_date: datetime) -> AsyncIterator[str]:
    """Get last fetched files path from cvelist repo"""
    async for json_item in _get_cve_changes_logs(f"{source_dir}/deltaLog.json"):
        if fetch_time_string := json_item.get("fetchTime"):
            if date_parser(fetch_time_string) < last_fetching_date:
                break

        new_files = _generate_file_paths(source_dir, json_item["new"])
        for file_path in new_files:
            yield "create", file_path

        updated_files = _generate_file_paths(source_dir, json_item["updated"])
        for file_path in updated_files:
            yield "update", file_path
