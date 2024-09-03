import os
import json
import logging
import subprocess
from datetime import datetime

from cvelist.config import settings

logger = logging.getLogger(__name__)

DATA_FOLDER = settings.DATA_FOLDER
SERVICE_INFO_FILE_NAME = settings.SERVICE_INFO_FILE_NAME
LAST_UPDATE_TIME_FIELD = settings.LAST_UPDATE_TIME_FIELD

REPO_SUCCESSFULLY_CLONED = 1
REPO_CLONING_SKIPPED = 0


class GitClientException(Exception):
    ...


def _repo_exists(repo_name: str) -> bool:
    return os.path.exists(f"{DATA_FOLDER}/{repo_name}")


def _service_info_file_exists() -> bool:
    return os.path.exists(f"{DATA_FOLDER}/{SERVICE_INFO_FILE_NAME}")


def _load_service_info_file(data: dict | None = None):
    if not data:
        data = {LAST_UPDATE_TIME_FIELD: None}

    with open(f"{DATA_FOLDER}/{SERVICE_INFO_FILE_NAME}", "w") as f:
        f.write(json.dumps(data))


def get_service_info() -> dict:
    with open(f"{DATA_FOLDER}/{SERVICE_INFO_FILE_NAME}", "r") as f:
        return json.loads(f.read())
    

def update_last_fetching_date(value: datetime) -> None:
    _load_service_info_file(
        {LAST_UPDATE_TIME_FIELD: value.strftime(settings.DATE_TIME_FORMAT)}
    )


def clone_repository(repo_name: str, repo_url: str) -> int:
    print("Git: Start cloning repository")
    if _repo_exists(repo_name):
        logger.info(f"Repository {repo_name} has been already cloned")
        return REPO_CLONING_SKIPPED

    result = subprocess.run(["git", "clone", repo_url,  "--depth=1"], cwd=DATA_FOLDER)
    if result.returncode != 0:
        raise GitClientException("Something went wrong while cloning repository")

    _load_service_info_file()
    print("Git: Finish cloning repository")

    return REPO_SUCCESSFULLY_CLONED


def fetch_repository(repo_name: str) -> None:
    print("Git: Start fetching repository")
    if not _repo_exists(repo_name):
        raise GitClientException(f"Repository {repo_name} does not exist")
    
    if not _service_info_file_exists():
        raise GitClientException("service_info file was not found")
    
    service_info = get_service_info()
    if not service_info.get(LAST_UPDATE_TIME_FIELD):
        raise GitClientException("Service info last update time is missing")

    result = subprocess.run(["git", "pull"], cwd=f"{DATA_FOLDER}/{repo_name}")
    if result.returncode != 0:
        raise GitClientException("Something went wrong while fetching repository")
    print("Git: Finish fetching repository")
