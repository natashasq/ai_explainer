from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "AI Explainer Backend"
    VERSION: str = "1.0.0"
    debug: bool = True
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    class Config:
        env_file = ".env"


settings = Settings()
