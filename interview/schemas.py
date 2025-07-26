from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from interview.models import InterviewStatus, ResponseType, EvaluationScore

# Request schemas
class StartInterviewRequest(BaseModel):
    candidate_name: str = Field(..., min_length=1, description="Name of the candidate")
    candidate_email: Optional[str] = Field(None, description="Email of the candidate")
    topics: List[str] = Field(..., min_items=1, description="Topics/tags for question selection")
    total_questions: int = Field(..., ge=5, le=50, description="Total number of questions (5-50)")
    difficulty_level: Literal["easy", "medium", "hard", "mixed"] = Field(
        "mixed", description="Difficulty level for questions"
    )

class SubmitAnswerRequest(BaseModel):
    session_id: str = Field(..., description="Interview session ID")
    answer: str = Field(..., min_length=1, description="Candidate's answer")
    selected_option: Optional[str] = Field(None, description="Selected option for MCQ questions")
    time_spent_seconds: Optional[int] = Field(None, ge=0, description="Time spent on question")

class ContinueConversationRequest(BaseModel):
    session_id: str = Field(..., description="Interview session ID") 
    message: str = Field(..., min_length=1, description="Candidate's message or clarification")

class GetNextQuestionRequest(BaseModel):
    session_id: str = Field(..., description="Interview session ID")

# Response schemas
class QuestionResponse(BaseModel):
    question_id: str
    question_text: str
    question_type: ResponseType
    options: Optional[List[str]] = None
    context: Optional[str] = None  # Additional context or follow-up from AI
    question_number: int
    total_questions: int

class InterviewSessionResponse(BaseModel):
    session_id: str
    candidate_name: str
    candidate_email: Optional[str] = None
    topics: List[str]
    total_questions: int
    difficulty_level: str
    status: InterviewStatus
    current_question_index: int
    started_at: datetime
    completed_at: Optional[datetime] = None

class SubmitAnswerResponse(BaseModel):
    success: bool
    message: str
    feedback: Optional[str] = None  # Immediate feedback from AI
    next_question: Optional[QuestionResponse] = None
    is_interview_complete: bool = False

class ConversationResponse(BaseModel):
    response: str
    next_question: Optional[QuestionResponse] = None
    is_clarification_needed: bool = False

class CandidateResponseDetails(BaseModel):
    question_id: str
    question_text: str
    question_type: ResponseType
    candidate_answer: str
    expected_answer: str
    selected_option: Optional[str] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    ai_feedback: Optional[str] = None
    time_spent_seconds: Optional[int] = None
    answered_at: datetime

class InterviewEvaluationResponse(BaseModel):
    session_id: str
    candidate_name: str
    overall_score: float
    performance_level: EvaluationScore
    
    # Detailed breakdown
    total_questions: int
    questions_answered: int
    questions_skipped: int
    mcq_score: Optional[float] = None
    descriptive_score: Optional[float] = None
    topic_scores: Dict[str, float] = {}
    
    # Timing and consistency
    average_response_time: Optional[float] = None
    consistency_score: Optional[float] = None
    communication_quality: Optional[float] = None
    
    # AI insights
    performance_summary: Optional[str] = None
    detailed_analysis: Optional[str] = None
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    recommendations: List[str] = []
    
    # Metadata
    interview_duration_minutes: Optional[int] = None
    completed_at: Optional[datetime] = None

class InterviewSummaryResponse(BaseModel):
    session_id: str
    candidate_name: str
    status: InterviewStatus
    overall_score: Optional[float] = None
    performance_level: Optional[EvaluationScore] = None
    questions_answered: int
    total_questions: int
    started_at: datetime
    completed_at: Optional[datetime] = None

class InterviewHistoryResponse(BaseModel):
    session_id: str
    candidate_name: str
    responses: List[CandidateResponseDetails]
    conversation_highlights: List[Dict[str, Any]] = []

# Administrative schemas
class InterviewStatsResponse(BaseModel):
    total_interviews: int
    active_interviews: int
    completed_interviews: int
    average_score: float
    score_distribution: Dict[str, int]  # performance_level -> count
    popular_topics: Dict[str, int]  # topic -> count

class QuestionSelectionRequest(BaseModel):
    topics: List[str] = Field(..., min_items=1)
    count: int = Field(..., ge=1, le=50)
    difficulty_level: Literal["easy", "medium", "hard", "mixed"] = "mixed"
    exclude_questions: List[str] = Field([], description="Question IDs to exclude")

class QuestionSelectionResponse(BaseModel):
    questions: List[Dict[str, Any]]
    selection_strategy: str
    total_available: int

# Error responses
class InterviewErrorResponse(BaseModel):
    error: str
    detail: str
    session_id: Optional[str] = None

# Pagination
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool 