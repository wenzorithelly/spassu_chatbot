from app.clients.llm.copilot import CopilotClient
from app.entities.schema.agent_response_schema import SQLQueryResponse
import json


class SQLGeneratorAgent(CopilotClient):
    def __init__(self, tenant_id: str, client_id: str):
        super().__init__(tenant_id, client_id)

    async def generate_sql_query(self, user_message: str, system_prompt: str) -> SQLQueryResponse:
        """Generate SQL query from user message"""
        messages = [
            {
                "role": "system",
                "content": f"{system_prompt}\n\nRespond in JSON format: {json.dumps(SQLQueryResponse.model_json_schema())}"
            },
            {
                "role": "user",
                "content": f"Generate SQL for: {user_message}"
            }
        ]

        response = await self._call_api(messages)
        return SQLQueryResponse.model_validate_json(response)

    async def _call_api(self, messages):
        """Call the base client API"""
        return await super().get_response(messages)