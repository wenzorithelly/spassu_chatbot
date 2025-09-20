from sqlalchemy.orm import Session
from typing import Optional
from app.entities.repositories.base_repository import BaseRepository
from app.entities.models.chat_sessions import ChatSessionModel
from app.entities.schema.chat_sessions_schema import (
    ChatSessionCreateSchema,
    ChatSessionUpdateSchema,
    ChatSessionSchema,
)


class ChatSessionsRepository(
    BaseRepository[ChatSessionModel, ChatSessionCreateSchema, ChatSessionUpdateSchema]
):
    def get_by_user_email(
        self, db: Session, user_email: str
    ) -> Optional[ChatSessionSchema]:
        """Get a chat session by user_email"""
        db_obj = (
            db.query(self.model).filter(self.model.user_email == user_email).first()
        )
        if not db_obj:
            return None
        return self.model_schema.model_validate(db_obj)
