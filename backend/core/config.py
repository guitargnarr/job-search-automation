"""
Configuration management for the automation platform
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Job Search Automation Platform"
    VERSION: str = "2.0.0"

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./job_search.db",
        env="DATABASE_URL"
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email Settings (Gmail API)
    GMAIL_CREDENTIALS_FILE: Optional[str] = Field(
        default=None,
        env="GMAIL_CREDENTIALS_FILE"
    )
    GMAIL_TOKEN_FILE: Optional[str] = Field(
        default=None,
        env="GMAIL_TOKEN_FILE"
    )
    GMAIL_SCOPES: Optional[str] = Field(
        default=None,
        env="GMAIL_SCOPES"
    )

    @property
    def gmail_scopes_list(self) -> List[str]:
        """Get Gmail scopes as a list"""
        if self.GMAIL_SCOPES:
            return self.GMAIL_SCOPES.split(",")
        return [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.labels"
        ]

    # LinkedIn Settings - DEPRECATED
    # LINKEDIN_EMAIL: Optional[str] = Field(default=None, env="LINKEDIN_EMAIL")
    # LINKEDIN_PASSWORD: Optional[str] = Field(default=None, env="LINKEDIN_PASSWORD")
    # LINKEDIN_HEADLESS: bool = Field(default=True, env="LINKEDIN_HEADLESS")
    # LINKEDIN_MAX_CONNECTIONS_PER_DAY: int = 20

    # OpenAI Settings - DEPRECATED
    # OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    # OPENAI_MODEL: str = "gpt-4-turbo-preview"
    # OPENAI_TEMPERATURE: float = 0.7

    # Job Search Settings
    JOB_SEARCH_KEYWORDS: str = Field(
        default="business analyst,data analyst,healthcare analyst",
        env="JOB_SEARCH_KEYWORDS"
    )
    JOB_SEARCH_LOCATION: str = "Louisville, KY"
    JOB_SEARCH_RADIUS: int = 50  # miles

    @property
    def job_search_keywords_list(self) -> List[str]:
        """Get job search keywords as a list"""
        return [k.strip() for k in self.JOB_SEARCH_KEYWORDS.split(",")]

    # Application Settings
    APPLICATIONS_DIR: str = Field(
        default=str(Path.home() / "Desktop" / "Job_Search" / "applications"),
        env="APPLICATIONS_DIR"
    )
    TEMPLATES_DIR: str = Field(
        default=str(Path.home() / "Desktop" / "Job_Search" / "documents"),
        env="TEMPLATES_DIR"
    )
    MAX_APPLICATIONS_PER_DAY: int = 10

    # Redis Settings (for task queue)
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/1", env="CELERY_RESULT_BACKEND")

    # Automation Settings
    AUTO_FOLLOW_UP_DAYS: str = Field(default="7,14,21", env="AUTO_FOLLOW_UP_DAYS")
    ATS_MINIMUM_SCORE: int = Field(default=70, env="ATS_MINIMUM_SCORE")
    EMAIL_CHECK_INTERVAL_MINUTES: int = Field(default=30, env="EMAIL_CHECK_INTERVAL_MINUTES")
    JOB_AGGREGATION_INTERVAL_HOURS: int = Field(default=6, env="JOB_AGGREGATION_INTERVAL_HOURS")

    # API Pagination Limits (prevent memory exhaustion)
    MAX_API_PAGE_SIZE: int = Field(default=100, env="MAX_API_PAGE_SIZE")
    DEFAULT_API_PAGE_SIZE: int = Field(default=50, env="DEFAULT_API_PAGE_SIZE")

    @property
    def auto_follow_up_days_list(self) -> List[int]:
        """Get follow-up days as a list of integers"""
        return [int(d.strip()) for d in self.AUTO_FOLLOW_UP_DAYS.split(",")]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "job_automation.log"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Create settings instance
settings = Settings()

# Ensure required directories exist
Path(settings.APPLICATIONS_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.TEMPLATES_DIR).mkdir(parents=True, exist_ok=True)
