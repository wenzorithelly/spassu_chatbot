from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.clients.llm.azure_openai import AzureOpenAIClient
from app.entities.schema.agent_response_schema import ChatResponse
from app.agents.prompts import RESPONSE_GENERATOR_PROMPT
import json


class ResponseGeneratorAgent:
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = AzureOpenAIClient()

    async def generate_response(
        self,
        user_message: str,
        sql_results: str,
        message_history: List[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """Generate natural language response from SQL results with message history"""
        messages = [
            {
                "role": "system",
                "content": f"{RESPONSE_GENERATOR_PROMPT}\n\nRespond in JSON format: {json.dumps(ChatResponse.model_json_schema())}",
            }
        ]

        # Add message history if provided
        if message_history:
            messages.extend(message_history)

        messages.append(
            {
                "role": "user",
                "content": f"User asked: {user_message}\nSQL Results: {sql_results}\nGenerate response:",
            }
        )

        response = await self.llm_client.get_response_async(messages)
        # Clean response - remove markdown code blocks if present
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]  # Remove ```
        cleaned_response = cleaned_response.strip()

        return ChatResponse.model_validate_json(cleaned_response)
