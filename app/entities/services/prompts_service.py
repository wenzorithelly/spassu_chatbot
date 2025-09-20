from app.entities.models.prompts import PromptModel, PromptType
from app.entities.repositories.prompts_repo import PromptsRepo
from sqlalchemy.orm import Session


class PromptsService:
    def __init__(self, db: Session):
        self.db = db
        self.prompts_repo = PromptsRepo(db)

    def get_prompt_by_type(self, type: PromptType) -> PromptModel:
        return self.prompts_repo.get_prompt_by_type(type)

    def get_latest_prompt_by_type(self, type: PromptType) -> PromptModel:
        return self.prompts_repo.get_latest_prompt_by_type(type)

    def create_prompt(self, prompt: PromptModel) -> PromptModel:
        return self.prompts_repo.create_prompt(prompt)

    def update_prompt(self, prompt: PromptModel) -> PromptModel:
        return self.prompts_repo.update_prompt(prompt)
