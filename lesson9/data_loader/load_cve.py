import asyncio
from datetime import datetime, UTC

from cvelist.config import settings
from cvelist.load import load_cve
from cvelist.git_client.client import (
    DATA_FOLDER,
    REPO_SUCCESSFULLY_CLONED,
    clone_repository,
    update_last_fetching_date,
    fetch_repository,
    get_service_info,
)
from cvelist.git_client.directory_parser import get_files, get_new_fetched_files


async def main():
    loop = asyncio.get_running_loop()

    cloning_datetime = datetime.now(UTC)
    status = await loop.run_in_executor(
        None,
        clone_repository,
        settings.CVE_LIST_REPO_NAME,
        settings.CVE_LIST_REPO_URL
    )

    if status == REPO_SUCCESSFULLY_CLONED:
        print("Start SVE initialization")
        await load_cve(
            get_files(
                f"{DATA_FOLDER}/{settings.CVE_LIST_REPO_NAME}/{settings.CVE_LIST_REPO_ROOT_FOLDER}"
            )
        )
        await loop.run_in_executor(None, update_last_fetching_date, cloning_datetime)
        await asyncio.sleep(settings.FETCH_REPO_DELAY)

    while True:
        fetching_datetime = datetime.now(UTC)

        await loop.run_in_executor(None, fetch_repository, settings.CVE_LIST_REPO_NAME)

        service_info = await loop.run_in_executor(None, get_service_info)
        last_fetching_date_string = service_info[settings.LAST_UPDATE_TIME_FIELD]
        last_fetching_date_time = datetime.strptime(last_fetching_date_string, settings.DATE_TIME_FORMAT)

        _ = asyncio.create_task(
            load_cve(
                get_new_fetched_files(
                    (
                        f"{DATA_FOLDER}"
                        f"/{settings.CVE_LIST_REPO_NAME}"
                        f"/{settings.CVE_LIST_REPO_ROOT_FOLDER}"
                    ),
                    last_fetching_date_time
                ),
                extractor_workers_number=settings.FETCHING_EXTRACTOR_WORKERS_NUMBER,
                loader_workers_number=settings.FETCHING_LOADER_WORKERS_NUMBER,
                fetching=True,
            )
        )
        await loop.run_in_executor(None, update_last_fetching_date, fetching_datetime)
        print(f"Main: Sleeping for {settings.FETCH_REPO_DELAY} seconds")
        await asyncio.sleep(settings.FETCH_REPO_DELAY)


if __name__ == "__main__":
    asyncio.run(main())
