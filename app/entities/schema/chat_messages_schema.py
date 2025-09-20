from pydantic import BaseModel
from datetime import datetime


class ChatMessageBaseSchema(BaseModel):
    session_id: int
    role: str
    content: str


class ChatMessageCreateSchema(ChatMessageBaseSchema):
    pass


class ChatMessageUpdateSchema(ChatMessageCreateSchema):
    id: int


class ChatMessageSchema(ChatMessageUpdateSchema):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
