from sqlalchemy.orm import Session
from app.entities.repositories.chat_sessions_repo import ChatSessionsRepository
from app.entities.schema.chat_sessions_schema import (
    ChatSessionCreateSchema,
    ChatSessionUpdateSchema,
    ChatSessionSchema,
)


class ChatSessionsService:
    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = ChatSessionsRepository(db)

    def get_by_user_email(self, user_email: str) -> ChatSessionSchema:
        return self.repository.get_by_user_email(self.db, user_email)

    def create(self, create_schema: ChatSessionCreateSchema) -> ChatSessionSchema:
        return self.repository.create(self.db, create_schema)

    def update(self, update_schema: ChatSessionUpdateSchema) -> ChatSessionSchema:
        return self.repository.update_by_id(self.db, update_schema)

    def delete(self, id: int) -> ChatSessionSchema:
        return self.repository.remove_by_id(self.db, id)
