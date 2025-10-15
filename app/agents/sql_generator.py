from sqlalchemy.orm import Session
from app.clients.llm.azure_openai import AzureOpenAIClient
from app.entities.schema.agent_response_schema import SQLQueryResponse
from app.agents.prompts import SQL_GENERATOR_PROMPT
import json


class SQLGeneratorAgent:
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = AzureOpenAIClient()

    async def generate_sql_query(
        self, user_message: str
    ) -> SQLQueryResponse:
        """Generate SQL query from user message"""
        messages = [
            {
                "role": "system",
                "content": f"{SQL_GENERATOR_PROMPT}\n\nRespond in JSON format: {json.dumps(SQLQueryResponse.model_json_schema())}",
            },
            {"role": "user", "content": f"Generate SQL for: {user_message}"},
        ]

        response = await self.llm_client.get_response_async(messages)
        # Clean response - remove markdown code blocks if present
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]  # Remove ```
        cleaned_response = cleaned_response.strip()

        return SQLQueryResponse.model_validate_json(cleaned_response)
