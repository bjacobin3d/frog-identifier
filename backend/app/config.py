from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    app_name: str = "Frog Identifier API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "frog_user"
    db_password: str = "frog_password"
    db_name: str = "frog_identifier"
    
    # File storage
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # ML Model paths
    audio_model_path: str = "models/audio_classifier.pt"
    image_model_path: str = "models/image_classifier.pt"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    @property
    def database_url(self) -> str:
        """Generate async database URL."""
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def sync_database_url(self) -> str:
        """Generate sync database URL for Alembic."""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
