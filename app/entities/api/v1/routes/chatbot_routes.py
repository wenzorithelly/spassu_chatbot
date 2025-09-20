from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.clients.db.postgres_client import get_db
from app.entities.schema.chat_messages_schema import ChatMessageSchema
from app.entities.services.conversations_service import ConversationsService
from app.monitoring.logging import get_logger

logger = get_logger(__name__)

chatbot_router = APIRouter()


def get_conversations_service(db: Session = Depends(get_db)) -> ConversationsService:
    return ConversationsService(db)


@chatbot_router.get("/answer", response_model=ChatMessageSchema)
def answer(
    message: str,
    user_email: str,
    conversations_service: ConversationsService = Depends(get_conversations_service),
):
    logger.info(f"Received message: {message} for user: {user_email}")
    return conversations_service.answer(message, user_email)
