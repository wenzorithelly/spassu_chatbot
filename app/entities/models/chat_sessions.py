from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.clients.db.postgres_client import Base


class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with messages
    messages = relationship(
        "ChatMessageModel", back_populates="session", cascade="all, delete-orphan"
    )

    @classmethod
    def create_session(
        cls,
        user_email=None,
        metadata=None,
    ):
        return cls(
            user_email=user_email,
            meta_data=metadata,
        )
