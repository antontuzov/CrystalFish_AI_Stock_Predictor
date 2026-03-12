"""
CrystalFish Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "CrystalFish"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/crystalfish"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@postgres:5432/crystalfish"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_BROKER_URL: str = "redis://redis:6379/1"
    
    # JWT
    JWT_SECRET_KEY: str = "your-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "mistralai/mistral-7b-instruct:free"
    OPENROUTER_FALLBACK_MODELS: List[str] = [
        "meta-llama/llama-3-8b-instruct:free",
        "google/gemma-2b-it:free",
    ]
    OPENROUTER_RATE_LIMIT_DELAY: float = 1.0  # seconds between requests
    
    # Simulation
    MAX_AGENTS_PER_SIMULATION: int = 500
    DEFAULT_AGENTS_COUNT: int = 100
    SIMULATION_MAX_STEPS: int = 90
    SIMULATION_TIMEOUT_MINUTES: int = 30
    
    # External APIs
    YAHOO_FINANCE_ENABLED: bool = True
    COINGECKO_API_KEY: Optional[str] = None
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://frontend:80",
    ]
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings