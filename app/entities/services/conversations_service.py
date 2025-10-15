from typing import List
from app.entities.schema.chat_sessions_schema import (
    ChatSessionSchema,
    ChatSessionCreateSchema,
    ChatSessionUpdateSchema,
)
from sqlalchemy.orm import Session
from app.entities.services.chat_sessions_service import ChatSessionsService
from app.entities.services.chat_messages_service import ChatMessagesService
from app.entities.schema.chat_messages_schema import (
    ChatMessageCreateSchema,
    ChatMessageSchema,
)
from app.agents.sql_generator import SQLGeneratorAgent
from app.agents.response_generator import ResponseGeneratorAgent
from app.clients.db.azure_sql_client import AzureSQLClient
from app.monitoring.logging import get_logger

logger = get_logger(__name__)


class ConversationsService:
    def __init__(self, db: Session):
        self.db = db
        self.chat_sessions_service = ChatSessionsService(db)
        self.chat_messages_service = ChatMessagesService(db)
        self.sql_generator_agent = SQLGeneratorAgent(db)
        self.response_generator_agent = ResponseGeneratorAgent(db)
        self.azure_sql_client = AzureSQLClient()

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

    async def generate_sql_query(self, message: str) -> str:
        sql_response = await self.sql_generator_agent.generate_sql_query(message)
        return sql_response.query

    async def generate_response(
        self, message: str, sql_results: str, message_history: List[ChatMessageSchema]
    ) -> str:
        response = await self.response_generator_agent.generate_response(
            user_message=message,
            sql_results=sql_results,
            message_history=message_history,
        )
        return response.response

    async def answer(self, message: str, user_email: str) -> str:
        # Generate SQL query
        sql_query = await self.generate_sql_query(message)
        logger.info(f"Generated SQL Query: {sql_query}")

        # Execute SQL query against Azure SQL Database
        query_result = self.azure_sql_client.execute_query_safe(sql_query)
        logger.info(f"Query execution result: {query_result}")

        # Format query results for the AI
        if query_result["success"]:
            formatted_results = {
                "success": True,
                "row_count": query_result["row_count"],
                "data": query_result["data"][:10],  # Limit to first 10 rows for AI processing
                "columns": query_result.get("columns", [])
            }
        else:
            formatted_results = {
                "success": False,
                "error": query_result["error"],
                "data": []
            }

        # Get conversation context
        conversation = self.get_conversation_by_user_email(user_email=user_email)
        logger.info(f"Conversation: {conversation}")

        # Generate natural language response
        response = await self.generate_response(
            message=message,
            sql_results=str(formatted_results),
            message_history=conversation.messages if conversation else [],
        )
        logger.info(f"Final Response: {response}")
        return response
