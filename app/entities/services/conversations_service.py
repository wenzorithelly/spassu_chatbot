from typing import List
from app.entities.schema.chat_sessions_schema import (
    ChatSessionSchema,
    ChatSessionCreateSchema,
    ChatSessionUpdateSchema,
)
from app.entities.services.prompts_service import PromptsService
from sqlalchemy.orm import Session
from app.entities.services.chat_sessions_service import ChatSessionsService
from app.entities.services.chat_messages_service import ChatMessagesService
from app.entities.schema.chat_messages_schema import (
    ChatMessageCreateSchema,
    ChatMessageSchema,
)
from app.agents.sql_generator import SQLGeneratorAgent
from app.agents.response_generator import ResponseGeneratorAgent
from app.entities.models.prompts import PromptType
from app.monitoring.logging import get_logger

logger = get_logger(__name__)


class ConversationsService:
    def __init__(self, db: Session):
        self.db = db
        self.chat_sessions_service = ChatSessionsService(db)
        self.chat_messages_service = ChatMessagesService(db)
        self.sql_generator_agent = SQLGeneratorAgent(db)
        self.response_generator_agent = ResponseGeneratorAgent(db)
        self.prompts_service = PromptsService(db)

    def get_conversation_by_user_email(self, user_email: str) -> ChatSessionSchema:
        return self.chat_sessions_service.get_by_user_email(user_email)

    def create_conversation(
        self, create_schema: ChatSessionCreateSchema
    ) -> ChatSessionSchema:
        return self.chat_sessions_service.create(create_schema)

    def update_conversation(
        self, update_schema: ChatSessionUpdateSchema
    ) -> ChatSessionSchema:
        return self.chat_sessions_service.update(update_schema)

    def add_message_to_conversation(
        self, message_schema: ChatMessageCreateSchema
    ) -> ChatMessageSchema:
        return self.chat_messages_service.create(message_schema)

    def generate_sql_query(self, message: str) -> ChatMessageSchema:
        prompt = self.prompts_service.get_latest_prompt_by_type(
            PromptType.SQL_GENERATOR
        )
        sql_query = self.sql_generator_agent.generate_sql_query(message, prompt.prompt)
        return sql_query

    def generate_response(
        self, message: str, sql_query: str, message_history: List[ChatMessageSchema]
    ) -> ChatMessageSchema:
        prompt = self.prompts_service.get_latest_prompt_by_type(
            PromptType.RESPONSE_GENERATOR
        )
        response = self.response_generator_agent.generate_response(
            user_message=message,
            sql_results=sql_query,
            system_prompt=prompt.prompt,
            message_history=message_history,
        )
        return response

    def answer(self, message: str, user_email: str) -> ChatMessageSchema:
        sql_query = self.generate_sql_query(message)
        logger.info(f"SQL Query: {sql_query}")
        conversation = self.get_conversation_by_user_email(user_email=user_email)
        logger.info(f"Conversation: {conversation.model_dump(mode='json')}")
        response = self.generate_response(
            message=message, sql_query=sql_query, message_history=conversation.messages
        )
        logger.info(f"Response: {response.model_dump(mode='json')}")
        return response
