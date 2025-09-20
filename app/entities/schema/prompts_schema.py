from pydantic import BaseModel
from datetime import datetime
from app.entities.models.prompts import PromptType


class PromptBaseSchema(BaseModel):
    type: PromptType
    prompt: str
    is_active: bool = True


class PromptCreateSchema(PromptBaseSchema):
    pass


class PromptUpdateSchema(PromptCreateSchema):
    id: int


class PromptSchema(PromptUpdateSchema):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True