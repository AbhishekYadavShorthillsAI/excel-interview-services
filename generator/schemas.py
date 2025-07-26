from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal, Any
from datetime import datetime


class ChatHistoryRequest(BaseModel):
    history: List[Dict[str, Any]] 
    query: str

class ChatHistoryResponse(BaseModel):
    history: List[Dict[str, Any]]

class QuestionResponse(BaseModel):
    id: str
    question: str
    answer: str
    question_type: str  # "mcq" or "descriptive"
    options: Optional[List[str]] = None
    topic: str  # This maps to the 'tag' field in the model
    tag: str
    created_at: Optional[datetime] = None

class QuestionCreate(BaseModel):
    question: str = Field(..., min_length=1, description="The interview question")
    answer: str = Field(..., min_length=1, description="The answer to the question")
    question_type: Literal["mcq", "descriptive"] = Field(..., description="Type of question")
    options: Optional[List[str]] = Field(None, description="Options for MCQ questions")
    tag: str = Field(..., min_length=1, description="Category/tag for the question")

class QuestionGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="The topic for question generation")
    number: int = Field(..., ge=1, le=50, description="Number of questions to generate (1-50)")
    question_type: Literal["mcq", "descriptive", "mixed"] = Field(..., description="Type of questions to generate")
    
class GenerationResponse(BaseModel):
    success: bool
    message: str
    questions_generated: int = 0

class ErrorResponse(BaseModel):
    detail: str
