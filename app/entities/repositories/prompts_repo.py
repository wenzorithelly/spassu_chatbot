from app.entities.models.prompts import (
    PromptModel,
    PromptType,
)
from app.entities.schema.prompts_schema import PromptCreateSchema, PromptUpdateSchema
from app.entities.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session


class PromptsRepo(BaseRepository[PromptModel, PromptCreateSchema, PromptUpdateSchema]):
    def __init__(self, db: Session):
        super().__init__(db, PromptModel)

    def get_prompt_by_type(self, type: PromptType) -> PromptModel:
        return self.db.query(PromptModel).filter(PromptModel.type == type).first()

    def get_latest_prompt_by_type(self, type: PromptType) -> PromptModel:
        return (
            self.db.query(PromptModel)
            .filter(PromptModel.type == type)
            .order_by(PromptModel.created_at.desc())
            .first()
        )

    def create_prompt(self, prompt: PromptModel) -> PromptModel:
        self.create(prompt)
        return prompt

    def update_prompt(self, prompt: PromptModel) -> PromptModel:
        self.update_by_id(prompt.id, prompt)
        return prompt
