from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime

class Question(Document):
    question: str
    answer: str
    question_type: str  # "mcq" or "descriptive"
    options: Optional[List[str]] = None
    tag: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "questions"
