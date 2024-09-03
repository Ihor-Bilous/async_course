import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


class Settings:
    CVE_LIST_REPO_NAME: str = "cvelistV5"
    CVE_LIST_REPO_ROOT_FOLDER: str = "cves"
    CVE_LIST_REPO_URL: str = "https://github.com/CVEProject/cvelistV5"
    CVE_LIST_API_BASE_URL: str = "http://localhost:8000"

    DATA_FOLDER: str = "cvelist/data"
    SERVICE_INFO_FILE_NAME: str = "service_info.json"
    LAST_UPDATE_TIME_FIELD: str = "last_update_time"

    BULK_INSERT_BATCH_SIZE: int = int(os.getenv("BULK_INSERT_BATCH_SIZE", 1000))
    EXTRACTOR_WORKERS_NUMBER: int = int(os.getenv("EXTRACTOR_WORKERS_NUMBER", 40))
    LOADER_WORKERS_NUMBER: int = int(os.getenv("LOADER_WORKERS_NUMBER", 10))
    QUEUE_MAX_SIZE_COEFFICIENT: float = 1.5

    FETCHING_EXTRACTOR_WORKERS_NUMBER: int = int(os.getenv("FETCHING_EXTRACTOR_WORKERS_NUMBER"), 5)
    FETCHING_LOADER_WORKERS_NUMBER: int = int(os.getenv("FETCHING_LOADER_WORKERS_NUMBER"), 2)

    FETCH_REPO_DELAY: int = int(os.getenv("FETCH_REPO_DELAY", 180))  # 3 min

    DATE_TIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"


settings = Settings()
