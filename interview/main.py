from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
import logging
from dotenv import load_dotenv

# Import models from both generator and interview services
from generator.models import Question
from interview.models import (
    InterviewSession, CandidateResponse, InterviewEvaluation, QuestionPool
)
from interview.routes import router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Interview Service",
    description="""
    Intelligent Interview Conductor Service
    
    This service provides conversational AI-powered interviews with:
    - Intelligent question selection from existing question pools
    - Real-time conversational interview experience
    - AI-based response evaluation and scoring
    - Comprehensive performance analysis and reports
    - Adaptive difficulty based on candidate performance
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and setup"""
    try:
        # Get MongoDB connection string from environment
        mongo_url = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        database_name = os.getenv("MONGODB_DATABASE", "excel_interviewer")
        
        logger.info(f"Connecting to MongoDB at: {mongo_url}")
        
        # Create MongoDB client
        client = AsyncIOMotorClient(mongo_url)
        
        # Initialize Beanie with all document models
        document_models = [
            # Generator service models
            Question,
            # Interview service models  
            InterviewSession,
            CandidateResponse,
            InterviewEvaluation,
            QuestionPool
        ]
        
        await init_beanie(
            database=client[database_name], 
            document_models=document_models
        )
        
        logger.info("Database initialization completed successfully")
        
        # Verify connection by checking available questions
        question_count = await Question.count()
        logger.info(f"Found {question_count} questions available for interviews")
        
        if question_count == 0:
            logger.warning("No questions found in database. Make sure the generator service has created questions first.")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Interview service shutting down...")

# Include interview routes
app.include_router(router, prefix="/api/v1/interview", tags=["interview"])

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "AI Interview Service",
        "version": "1.0.0",
        "description": "Intelligent conversational interview system",
        "features": [
            "Smart question selection",
            "Conversational AI interviews", 
            "Real-time evaluation",
            "Performance analytics",
            "Comprehensive reports"
        ],
        "docs_url": "/docs",
        "endpoints": {
            "start_interview": "/api/v1/interview/start",
            "get_question": "/api/v1/interview/session/{session_id}/question",
            "submit_answer": "/api/v1/interview/session/{session_id}/answer",
            "get_evaluation": "/api/v1/interview/session/{session_id}/evaluation",
            "get_stats": "/api/v1/interview/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connectivity
        question_count = await Question.count()
        session_count = await InterviewSession.count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "questions_available": question_count,
            "total_sessions": session_count,
            "timestamp": os.environ.get("TIMESTAMP", "unknown")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/api/v1/interview")
async def interview_service_info():
    """Interview service specific information"""
    try:
        # Get service statistics
        stats = {
            "questions": {
                "total": await Question.count(),
                "mcq": await Question.find(Question.question_type == "mcq").count(),
                "descriptive": await Question.find(Question.question_type == "descriptive").count()
            },
            "sessions": {
                "total": await InterviewSession.count(),
                "active": await InterviewSession.find(InterviewSession.status == "active").count(),
                "completed": await InterviewSession.find(InterviewSession.status == "completed").count()
            },
            "evaluations": {
                "total": await InterviewEvaluation.count()
            }
        }
        
        # Get available topics
        questions = await Question.find_all().to_list()
        topics = list(set(q.tag for q in questions))
        
        return {
            "service": "Interview Service",
            "capabilities": [
                "Intelligent question selection",
                "Conversational interviews",
                "AI-powered evaluation", 
                "Performance analytics",
                "Adaptive difficulty"
            ],
            "statistics": stats,
            "available_topics": sorted(topics),
            "supported_question_types": ["mcq", "descriptive"],
            "difficulty_levels": ["easy", "medium", "hard", "mixed", "adaptive"]
        }
        
    except Exception as e:
        logger.error(f"Error getting service info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving service information")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "detail": "The requested resource was not found",
        "suggestion": "Check the API documentation at /docs for available endpoints"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error", 
        "detail": "An unexpected error occurred",
        "suggestion": "Please try again later or contact support if the problem persists"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))  # Different port from generator service
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Interview Service on {host}:{port}")
    
    uvicorn.run(
        "interview.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    ) 