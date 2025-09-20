from pydantic import BaseModel


class SQLQueryResponse(BaseModel):
    query: str
    explanation: str


class ChatResponse(BaseModel):
    response: str