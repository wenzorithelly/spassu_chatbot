from typing import List
from sqlalchemy.orm import Session
from app.entities.repositories.chat_messages_repo import ChatMessageRepository
from app.entities.schema.chat_messages_schema import (
    ChatMessageCreateSchema,
    ChatMessageUpdateSchema,
    ChatMessageSchema,
)


class ChatMessagesService:
    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = ChatMessageRepository(db)

    def get_by_session_id(self, session_id: int) -> List[ChatMessageSchema]:
        return self.repository.get_by_session_id(self.db, session_id)

    def create(self, create_schema: ChatMessageCreateSchema) -> ChatMessageSchema:
        return self.repository.create(self.db, create_schema)

    def update(self, update_schema: ChatMessageUpdateSchema) -> ChatMessageSchema:
        return self.repository.update_by_id(self.db, update_schema)

    def delete(self, id: int) -> ChatMessageSchema:
        return self.repository.remove_by_id(self.db, id)
