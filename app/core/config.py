from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Render automatically provides DATABASE_URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Fix for SQLAlchemy (Render uses postgres:// but SQLAlchemy needs postgresql://)
    @property
    def SQLALCHEMY_DATABASE_URL(self):
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DataLog API"
    
    # CORS - Update with your frontend URL
    BACKEND_CORS_ORIGINS: list[str] = ["https://datalog-frontend.onrender.com/"]  # Change to your frontend URL in production

settings = Settings()
