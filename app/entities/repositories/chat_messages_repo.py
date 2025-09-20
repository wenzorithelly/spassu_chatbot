from sqlalchemy.orm import Session
from typing import List
from app.entities.models.chat_messages import ChatMessageModel
from app.entities.repositories.base_repository import BaseRepository
from app.entities.schema.chat_messages_schema import (
    ChatMessageCreateSchema,
    ChatMessageUpdateSchema,
    ChatMessageSchema,
)


class ChatMessageRepository(
    BaseRepository[ChatMessageModel, ChatMessageCreateSchema, ChatMessageUpdateSchema]
):
    def __init__(self):
        super().__init__(ChatMessageModel, ChatMessageSchema)

    def get_by_session_id(
        self, db: Session, session_id: int
    ) -> List[ChatMessageSchema]:
        """Get all messages for a specific session"""
        return [
            self.model_schema.model_validate(obj)
            for obj in db.query(self.model)
            .filter(self.model.session_id == session_id)
            .order_by(self.model.created_at.asc())
            .all()
        ]
