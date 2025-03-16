import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent
    PATH_TO_DB: str = str(BASE_DIR / "database" / "source" / "notes.db")
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
