from typing import Dict, Any, List
from openai import AzureOpenAI
from app.core.config import settings


class AzureOpenAIClient:
    def __init__(self):
        # Extract deployment name from endpoint URL
        endpoint_url = settings.AZURE_OPENAI_ENDPOINT
        if "/deployments/" in endpoint_url:
            self.deployment_name = endpoint_url.split("/deployments/")[1].split("/")[0]
            self.azure_endpoint = endpoint_url.split("/openai/deployments/")[0]
        else:
            raise ValueError("Could not extract deployment name from endpoint URL")

        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=self.azure_endpoint,
        )

    def test_connection(self) -> Dict[str, Any]:
        """Test if the Azure OpenAI connection works"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            return {
                "success": True,
                "message": "Connection successful",
                "deployment": self.deployment_name,
                "endpoint": self.azure_endpoint,
                "response": response.choices[0].message.content,
            }
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}"}

    def get_response(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Generate a response using Azure OpenAI"""
        try:
            # Default parameters
            params = {
                "model": self.deployment_name,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1.0),
            }

            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def get_response_async(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Async version of get_response for compatibility"""
        return self.get_response(messages, **kwargs)
