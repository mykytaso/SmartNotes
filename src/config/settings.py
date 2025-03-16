from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent
    PATH_TO_DB: str = str(BASE_DIR / "database" / "source" / "notes.db")
    DEBUG: bool = False
    GOOGLE_API_KEY: str = ""

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")


settings = Settings()
