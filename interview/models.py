from beanie import Document
from pydantic import Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class InterviewStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class ResponseType(str, Enum):
    MCQ = "mcq"
    DESCRIPTIVE = "descriptive"

class EvaluationScore(str, Enum):
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%
    AVERAGE = "average"     # 50-69%
    POOR = "poor"          # 0-49%

class CandidateResponse(Document):
    """Individual response to a question during an interview"""
    interview_session_id: str
    question_id: str
    question_text: str
    question_type: ResponseType
    candidate_answer: str
    expected_answer: str
    options: Optional[List[str]] = None  # For MCQ questions
    selected_option: Optional[str] = None  # For MCQ answers
    
    # Evaluation fields
    is_correct: Optional[bool] = None
    score: Optional[float] = None  # 0-100 scale
    evaluation_notes: Optional[str] = None
    ai_feedback: Optional[str] = None
    
    # Timing and metadata
    time_spent_seconds: Optional[int] = None
    answered_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "candidate_responses"

class InterviewSession(Document):
    """Complete interview session for a candidate"""
    candidate_name: str
    candidate_email: Optional[str] = None
    
    # Interview configuration
    topics: List[str]  # Tags/topics for question selection
    total_questions: int
    difficulty_level: str = "mixed"  # easy, medium, hard, mixed
    
    # Session state
    status: InterviewStatus = InterviewStatus.ACTIVE
    current_question_index: int = 0
    questions_asked: List[str] = []  # Question IDs
    
    # Conversation history for AI context
    conversation_history: List[Dict[str, Any]] = []
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_duration_minutes: Optional[int] = None
    
    # Overall evaluation
    overall_score: Optional[float] = None
    performance_level: Optional[EvaluationScore] = None
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    final_feedback: Optional[str] = None
    
    class Settings:
        name = "interview_sessions"

class InterviewEvaluation(Document):
    """Detailed evaluation and analytics for an interview session"""
    interview_session_id: str
    candidate_name: str
    
    # Question-wise analysis
    total_questions: int
    questions_answered: int
    questions_skipped: int
    
    # Score breakdown
    overall_score: float  # 0-100
    performance_level: Optional[EvaluationScore] = None
    mcq_score: Optional[float] = None
    descriptive_score: Optional[float] = None
    
    # Topic-wise performance
    topic_scores: Dict[str, float] = {}  # topic -> score
    
    # Detailed metrics
    average_response_time: Optional[float] = None
    consistency_score: Optional[float] = None  # How consistent answers are
    communication_quality: Optional[float] = None  # For descriptive answers
    
    # AI-generated insights
    performance_summary: Optional[str] = None
    detailed_analysis: Optional[str] = None
    recommendations: List[str] = []
    
    # Comparison metrics
    percentile_rank: Optional[float] = None  # Compared to other candidates
    
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "interview_evaluations"

class QuestionPool(Document):
    """Cache of questions selected for interview sessions with metadata"""
    session_id: str
    questions: List[Dict[str, Any]]  # Question details with selection metadata
    selection_strategy: str  # How questions were selected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "question_pools" 