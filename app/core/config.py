import os
from builtins import str
from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PG_USER: str = os.getenv("PG_USER")
    PG_PASS: str = os.getenv("PG_PASS")
    PG_HOST: str = os.getenv("PG_HOST")
    PG_PORT: int = os.getenv("PG_PORT")
    PG_DB: str = os.getenv("PG_DB")

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @computed_field
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


settings = Settings()
