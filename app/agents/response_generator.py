from typing import List, Dict, Any
from app.clients.llm.copilot import CopilotClient
from app.entities.schema.agent_response_schema import ChatResponse
import json


class ResponseGeneratorAgent(CopilotClient):
    def __init__(self, tenant_id: str, client_id: str):
        super().__init__(tenant_id, client_id)

    async def generate_response(
        self,
        user_message: str,
        sql_results: str,
        system_prompt: str,
        message_history: List[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """Generate natural language response from SQL results with message history"""
        messages = [
            {
                "role": "system",
                "content": f"{system_prompt}\n\nRespond in JSON format: {json.dumps(ChatResponse.model_json_schema())}",
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

        response = await self._call_api(messages)
        return ChatResponse.model_validate_json(response)

    async def _call_api(self, messages):
        """Call the base client API"""
        return await super().get_response(messages)
