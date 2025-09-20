import os

# import boto3
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from app.monitoring.logging import get_logger

logger = get_logger("config")


class Settings(BaseSettings):
    # Load environment variables from .env file and AWS Parameters
    load_dotenv()
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")
    API_V1_STR: str = "/api/v1"

    # Project Name
    PROJECT_NAME: str = "Spassu Chatbot"

    # Postgres
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    )


settings = Settings()
