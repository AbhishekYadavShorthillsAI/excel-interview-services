from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from generator.models import Question
from generator.routes import router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Excel Interview Question Generator", version="1.0.0")

@app.on_event("startup")
async def app_init():
    # Use environment variable for MongoDB connection
    mongo_url = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    await init_beanie(database=client["excel_interviewer"], document_models=[Question])

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Excel Interview Question Generator API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connectivity by counting questions
        question_count = await Question.count()
        return {
            "status": "healthy",
            "database": "connected", 
            "questions_available": question_count,
            "service": "generator"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "service": "generator"
        }
