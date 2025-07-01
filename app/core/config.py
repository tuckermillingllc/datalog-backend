from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DataLog API"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Render specific
    RENDER: Optional[bool] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
