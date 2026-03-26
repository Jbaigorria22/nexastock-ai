# src/api/routes/ai.py
from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from src.services.ai_service import get_ai_summary, get_copilot_answer

router = APIRouter()

class Question(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()

@router.get("/summary")
def ai_summary():
    return get_ai_summary()

@router.post("/copilot")
def copilot(q: Question):
    return get_copilot_answer(q.question)