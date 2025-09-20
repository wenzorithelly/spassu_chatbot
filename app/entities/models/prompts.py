from sqlalchemy import (
    Column,
    Text,
    DateTime,
    Integer,
    Boolean,
    Enum,
)
from sqlalchemy.sql import func
from app.clients.db.postgres_client import Base
import enum


class PromptType(enum.Enum):
    SQL_GENERATOR = "sql_generator"
    RESPONSE_GENERATOR = "response_generator"


class PromptModel(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(PromptType), nullable=False)
    prompt = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def create_prompt(cls, type: PromptType, prompt: str, is_active: bool = True):
        return cls(
            type=type,
            prompt=prompt,
            is_active=is_active,
        )