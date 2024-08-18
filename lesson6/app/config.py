import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    BULK_INSERT_BATCH_SIZE = int(os.getenv("BULK_INSERT_BATCH_SIZE", 2000))
    EXTRACTOR_WORKERS_NUMBER = int(os.getenv("EXTRACTOR_WORKERS_NUMBER", 40))
    LOADER_WORKERS_NUMBER = int(os.getenv("LOADER_WORKERS_NUMBER", 10))
    QUEUE_MAX_SIZE_COEFFICIENT = 1.5

    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = 5432
    DB_URI = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        db=POSTGRES_DB,
    )
