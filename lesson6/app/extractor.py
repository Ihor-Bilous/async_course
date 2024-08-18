import asyncio
import json
from datetime import datetime

import aiofiles

from .dtos import CveDTO


async def extractor_worker(
    worker_id: str,
    extractor_queue: asyncio.Queue,
    loader_queue: asyncio.Queue,
) -> None:
    print(f"Extractor worker #{worker_id} started")

    try:
        while True:
            file_path = await extractor_queue.get()
            if not file_path:
                extractor_queue.task_done()
                print(f"Extractor worker #{worker_id} is going to be closed")
                break

            cve = await _extract_cve(file_path)
            if cve:
                await loader_queue.put(cve)

            extractor_queue.task_done()
    except Exception as e:
        print(f"Error in Extractor worker #{worker_id}: {e}")
        raise e

    print(f"Extractor worker #{worker_id} is finished")


async def _read_file(file_path: str) -> dict:
    async with aiofiles.open(file_path, "r") as file:
        json_data = json.loads(await file.read())
    return json_data


async def _extract_cve(file_path: str) -> CveDTO | None:
    json_data = await _read_file(file_path)
    try:
        extractor = Extractor(json_data)
        return extractor.extract()
    except Exception as exc:
        print(f"File: {file_path} can not be parsed. Exception: {str(exc)}")
        return None


class Extractor:
    def __init__(self, json_data: dict) -> None:
        self._json_data = json_data

    def extract(self) -> CveDTO:
        return CveDTO(
            cve_id=self._extract_cve_id(),
            title=self._extract_title(),
            reserved_date=self._extract_reserved_date(),
            published_date=self._extract_published_date(),
            updated_date=self._extract_updated_date(),
            description=self._extract_description(),
            problem_types=self._extract_problem_types(),
        )

    @staticmethod
    def _date_parser(date_string: str) -> datetime:
        date_formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(date_string, date_format)
            except ValueError:
                continue

        raise ValueError(f"Time data '{date_string}' does not match any known format.")

    def _extract_cve_id(self) -> str:
        return self._json_data["cveMetadata"]["cveId"]

    def _extract_reserved_date(self) -> datetime:
        reserved_date_str = self._json_data["cveMetadata"].get("dateReserved")
        return self._date_parser(reserved_date_str) if reserved_date_str else None

    def _extract_published_date(self) -> datetime | None:
        published_date_str = self._json_data["cveMetadata"].get("datePublished")
        return self._date_parser(published_date_str) if published_date_str else None

    def _extract_updated_date(self) -> datetime:
        updated_date_str = self._json_data["cveMetadata"].get("dateUpdated")
        return self._date_parser(updated_date_str) if updated_date_str else None

    def _extract_title(self) -> str:
        containers_data = self._json_data["containers"]
        title_in_cna = (
            "cna" in containers_data
            and isinstance(containers_data["cna"], dict)
            and "title" in containers_data["cna"]
        )
        if title_in_cna:
            return containers_data["cna"]["title"]

        title_in_adp = (
            "adp" in containers_data
            and isinstance(containers_data["adp"], list)
            and len(containers_data["adp"]) > 0
            and "title" in containers_data["adp"][0]
        )
        if title_in_adp:
            return containers_data["adp"][0]["title"]

        return "Title not Found"

    def _extract_description(self) -> str:
        if "cna" not in self._json_data["containers"]:
            return ""

        cna = self._json_data["containers"]["cna"]
        if "descriptions" not in cna:
            return ""

        descriptions = [d["value"] for d in cna["descriptions"] if d["lang"] == "en"]
        if not descriptions:
            descriptions = [d["value"] for d in cna["descriptions"] if d["lang"] != "en"]
        return "\n".join(descriptions) if descriptions else ""

    def _extract_affected(self) -> list[str]:
        if "cna" not in self._json_data["containers"]:
            return []

        cna = self._json_data["containers"]["cna"]
        return [a["product"] for a in cna.get("affected", [])]

    def _extract_problem_types(self) -> str:
        if "cna" not in self._json_data["containers"]:
            return ""

        cna = self._json_data["containers"]["cna"]

        if "problemTypes" not in cna:
            return ""

        eng_problem_types = []
        other_land_problem_types = []
        for problem_type in cna["problemTypes"]:
            for desc in problem_type.get("descriptions", []):
                if "description" not in desc:
                    continue

                if "lang" in desc and desc["lang"] == "en":
                    eng_problem_types.append(desc["description"])
                elif "lang" in desc and desc["lang"] != "en":
                    other_land_problem_types.append(desc["description"])

        problem_types = eng_problem_types if eng_problem_types else other_land_problem_types
        return "\n".join(problem_types) if problem_types else ""
