from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "ARF API Control Plane"
    environment: str = "development"
    database_url: Optional[str] = None
    api_key: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
