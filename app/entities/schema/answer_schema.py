from pydantic import BaseModel


class AnswerSchema(BaseModel):
    message: str
    user_email: str
