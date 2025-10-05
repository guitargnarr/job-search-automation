"""
Configuration management for the automation platform
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Job Search Automation Platform"
    VERSION: str = "2.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./job_automation.db"  # SQLite for easy local dev
    # For production PostgreSQL:
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/jobsearch"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email Settings (Gmail API)
    GMAIL_CREDENTIALS_FILE: str = str(Path.home() / ".credentials" / "gmail_credentials.json")
    GMAIL_TOKEN_FILE: str = str(Path.home() / ".credentials" / "gmail_token.json")
    GMAIL_SCOPES: list = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.labels"
    ]

    # LinkedIn Settings
    LINKEDIN_EMAIL: Optional[str] = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD: Optional[str] = os.getenv("LINKEDIN_PASSWORD")
    LINKEDIN_HEADLESS: bool = True
    LINKEDIN_MAX_CONNECTIONS_PER_DAY: int = 20

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7

    # Job Search Settings
    JOB_SEARCH_KEYWORDS: list = ["business analyst", "data analyst", "healthcare analyst"]
    JOB_SEARCH_LOCATION: str = "Louisville, KY"
    JOB_SEARCH_RADIUS: int = 50  # miles

    # Application Settings
    APPLICATIONS_DIR: Path = Path.home() / "Desktop" / "Job_Search" / "applications"
    TEMPLATES_DIR: Path = Path.home() / "Desktop" / "Job_Search" / "documents"
    MAX_APPLICATIONS_PER_DAY: int = 10

    # Redis Settings (for task queue)
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Automation Settings
    AUTO_FOLLOW_UP_DAYS: list = [7, 14, 21]
    ATS_MINIMUM_SCORE: int = 70
    EMAIL_CHECK_INTERVAL_MINUTES: int = 30
    JOB_AGGREGATION_INTERVAL_HOURS: int = 6

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "job_automation.log"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure required directories exist
settings.APPLICATIONS_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)