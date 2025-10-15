from app.entities.models.prompts import (
    PromptModel,
    PromptType,
)
from app.entities.schema.prompts_schema import (
    PromptCreateSchema,
    PromptUpdateSchema,
    PromptSchema
)
from app.entities.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session


class PromptsRepo(BaseRepository[PromptModel, PromptCreateSchema, PromptUpdateSchema]):
    def __init__(self):
        super().__init__(PromptModel, PromptSchema)

    def get_prompt_by_type(self, db: Session, type: PromptType) -> PromptModel:
        return db.query(PromptModel).filter(PromptModel.type == type).first()

    def get_latest_prompt_by_type(self, db: Session, type: PromptType) -> PromptModel:
        return (
            db.query(PromptModel)
            .filter(PromptModel.type == type)
            .order_by(PromptModel.created_at.desc())
            .first()
        )

    def create_prompt(self, db: Session, prompt: PromptCreateSchema) -> PromptSchema:
        return self.create(db, prompt)

    def update_prompt(self, db: Session, prompt_id: int, prompt: PromptUpdateSchema) -> PromptSchema:
        return self.update_by_id(db, id=prompt_id, update_schema=prompt)
