from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.clients.db.postgres_client import get_db
from app.entities.schema.answer_schema import AnswerSchema
from app.entities.services.conversations_service import ConversationsService
from app.monitoring.logging import get_logger

logger = get_logger(__name__)

chatbot_router = APIRouter()


def get_conversations_service(db: Session = Depends(get_db)) -> ConversationsService:
    return ConversationsService(db)


@chatbot_router.post("/answer")
async def answer(
    payload: AnswerSchema,
    conversations_service: ConversationsService = Depends(get_conversations_service),
):
    logger.info(f"Received message: {payload.message} for user: {payload.user_email}")
    response = await conversations_service.answer(payload.message, payload.user_email)
    return {"response": response}
