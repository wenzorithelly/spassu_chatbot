from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any


class ChatSessionBaseSchema(BaseModel):
    user_email: str
    meta_data: Dict[str, Any]


class ChatSessionCreateSchema(ChatSessionBaseSchema):
    pass


class ChatSessionUpdateSchema(ChatSessionCreateSchema):
    id: int


class ChatSessionSchema(ChatSessionUpdateSchema):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
