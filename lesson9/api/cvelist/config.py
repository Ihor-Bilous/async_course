from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    BULK_CREATE_BATCH_SIZE: int = 1000

    @property
    def db_url(self):
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}".format(
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            db=self.POSTGRES_DB,
        )


settings = Settings()
