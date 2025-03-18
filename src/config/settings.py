import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent
    PATH_TO_DB: str = str(BASE_DIR / "database" / "source" / "notes.db")
    NLTK_DATA_PATH: str = str(BASE_DIR.parent / ".venv" / "nltk_data")
    ENVIRONMENT: str = "developing"
    DEBUG: bool = False
    GENAI_API_KEY: str = ""
    GENAI_MODEL: str = "gemini-2.0-flash"

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")


class TestingSettings(Settings):
    PATH_TO_DB: str = ":memory:"


def get_settings() -> BaseSettings:
    """
    Retrieve the application settings based on the environment.

    This function checks the `ENVIRONMENT` environment variable to determine
    which settings class to use. If `ENVIRONMENT` is set to `"testing"`, it
    returns an instance of `TestingSettings`. Otherwise, it defaults to `Settings`.

    """
    environment = os.getenv("ENVIRONMENT")

    if environment == "testing":
        return TestingSettings()
    elif environment == "developing":
        return Settings()
