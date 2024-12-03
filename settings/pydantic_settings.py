from pydantic import BaseModel, Field
from typing import List
import os


class Settings(BaseModel):
    # Django settings
    SECRET_KEY: str = Field(..., env="DJANGO_SECRET_KEY")
    INTERNAL_IPS: List[str] = Field(default=["127.0.0.1"])

    # Database settings
    DATABASES_ENGINE: str = "django.db.backends.postgresql"
    DATABASES_NAME: str = Field(..., env="POSTGRES_DB")
    DATABASES_USER: str = Field(..., env="POSTGRES_USER")
    DATABASES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    DATABASES_HOST: str = Field(..., env="POSTGRES_HOST", default="db")
    DATABASES_PORT: int = Field(..., env="POSTGRES_PORT", default=5432)

    # Redis settings
    REDIS_URL: str = Field(..., env="REDIS_URL", default="redis://redis:6379/5")

    # AWS settings
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME: str = Field(
        ..., env="AWS_STORAGE_BUCKET_NAME", default="project-stage"
    )

    # OpenAI settings
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_RETRY_ATTEMPTS: int = 3
    OPENAI_RETRY_WAIT_MULTIPLIER: int = 1
    OPENAI_RETRY_WAIT_MIN: int = 2
    OPENAI_RETRY_WAIT_MAX: int = 10

    # Social Auth settings
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY: str = Field(..., env="GOOGLE_OAUTH2_KEY")
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET: str = Field(..., env="GOOGLE_OAUTH2_SECRET")

    # Logging settings
    LOGGING_LEVEL: str = "INFO"
    LOGGING_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Adjustable time delay for scheduling
    SUMMARY_TASK_TIME_DELAY: int = 1

    class Config:
        # Load environment variables from a .env file
        env_file = ".env"


# Instantiate the settings class and load the settings
settings = Settings()

# Example of using the loaded settings
print(settings.SECRET_KEY)
print(settings.DATABASES_NAME)
print(settings.REDIS_URL)
