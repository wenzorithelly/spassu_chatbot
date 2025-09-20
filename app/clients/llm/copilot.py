from typing import Dict, Any, List
from azure.identity import DeviceCodeCredential, DefaultAzureCredential
from microsoft_agents_m365copilot_beta.agents_m365_copilot_beta_service_client import (
    AgentsM365CopilotBetaServiceClient,
)


class CopilotClient:
    def __init__(self, tenant_id: str, client_id: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client = None
        self.scopes = ["Files.Read.All", "Sites.Read.All", "Chat.ReadWrite"]

    async def authenticate(self):
        try:
            credentials = DefaultAzureCredential()
        except Exception:
            credentials = DeviceCodeCredential(
                tenant_id=self.tenant_id, client_id=self.client_id
            )

        self.client = AgentsM365CopilotBetaServiceClient(
            credentials=credentials, scopes=self.scopes
        )
        self.client.request_adapter.base_url = "https://graph.microsoft.com/beta"

    async def get_response(self, messages: List[Dict[str, Any]]) -> str:
        if not self.client:
            await self.authenticate()

        try:
            response = await self.client.copilot.chats.post(request_body=messages)
            return (
                response.choices[0].message.content
                if response.choices
                else "No response"
            )
        except Exception as e:
            return f"Error: {str(e)}"
