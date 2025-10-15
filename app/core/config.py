import os

# import boto3
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from app.monitoring.logging import get_logger

logger = get_logger(__name__)


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
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_RESOURCE_SECRET_ID: str = os.getenv("AZURE_RESOURCE_SECRET_ID")
    AZURE_RESOURCE_SECRET_KEY: str = os.getenv("AZURE_RESOURCE_SECRET_KEY")
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID")

    # Azure SQL Database
    AZURE_DB_HOST: str = os.getenv("AZURE_DB_HOST")
    AZURE_DATABASE: str = os.getenv("AZURE_DATABASE")
    AZURE_DB_USER: str = os.getenv("AZURE_DB_USER")
    AZURE_DB_PASSWORD: str = os.getenv("AZURE_DB_PASSWORD")

    # Azure Bot Service
    MICROSOFT_APP_ID: str = os.getenv("MICROSOFT_APP_ID", "")
    MICROSOFT_APP_PASSWORD: str = os.getenv("MICROSOFT_APP_PASSWORD", "")


settings = Settings()
