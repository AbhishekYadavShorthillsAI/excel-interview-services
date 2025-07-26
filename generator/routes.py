from fastapi import APIRouter, HTTPException, Query
from generator.schemas import (
    ChatHistoryRequest, QuestionResponse, QuestionGenerationRequest, 
    GenerationResponse, QuestionCreate, ErrorResponse, ChatHistoryResponse
)
from generator.handler.v1 import process_admin_conversation, generate_and_save
from generator.handler.common import fetch_questions_by_tag, save_questions_to_db
from generator.models import Question
from typing import List, Optional
import logging
import json

router = APIRouter()

@router.post("/chat")
async def chat_with_admin(request: ChatHistoryRequest):
    """Chat with the AI admin for question generation through conversation"""
    try:
        request_dict = request.model_dump() # Convert to simple dictionaries
        query = request_dict.get("query")
        history_dicts = request_dict.get("history")
        
        updated_history = await process_admin_conversation(history_dicts, query)


        return ChatHistoryResponse(history=updated_history)
        
    except Exception as e:
        logging.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing conversation: {str(e)}")

@router.post("/generate", response_model=GenerationResponse)
async def generate_questions_direct(request: QuestionGenerationRequest):
    """Direct endpoint to generate questions without conversation flow"""
    try:
        # Convert the request to the format expected by generate_and_save
        result_message = await generate_and_save(
            query=request.topic,
            tag=request.question_type,
            number=request.number
        )
        
        # Check if generation was successful
        if "successfully" in result_message.lower():
            return GenerationResponse(
                success=True,
                message=result_message,
                questions_generated=request.number
            )
        else:
            return GenerationResponse(
                success=False,
                message=result_message,
                questions_generated=0
            )
            
    except Exception as e:
        logging.error(f"Error in generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@router.get("/questions", response_model=List[QuestionResponse])
async def get_all_questions(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of questions returned"),
    skip: Optional[int] = Query(0, ge=0, description="Number of questions to skip")
):
    """Get all questions with optional pagination"""
    try:
        questions = await fetch_questions_by_tag()
        
        # Apply pagination
        if skip:
            questions = questions[skip:]
        if limit:
            questions = questions[:limit]
        
        return [QuestionResponse(
            id=str(q.id),
            question=q.question,
            answer=q.answer,
            question_type=q.question_type,
            options=q.options,
            topic=q.tag,  # Map tag to topic for response
            tag=q.tag,
            created_at=q.created_at
        ) for q in questions]
    except Exception as e:
        logging.error(f"Error fetching questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching questions: {str(e)}")

@router.get("/questions/by-tag/{tag}", response_model=List[QuestionResponse])
async def get_questions_by_tag(
    tag: str,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of questions returned"),
    skip: Optional[int] = Query(0, ge=0, description="Number of questions to skip")
):
    """Get questions filtered by tag with optional pagination"""
    try:
        questions = await fetch_questions_by_tag(tag)
        
        # Apply pagination
        if skip:
            questions = questions[skip:]
        if limit:
            questions = questions[:limit]
            
        return [QuestionResponse(
            id=str(q.id),
            question=q.question,
            answer=q.answer,
            question_type=q.question_type,
            options=q.options,
            topic=q.tag,
            tag=q.tag,
            created_at=q.created_at
        ) for q in questions]
    except Exception as e:
        logging.error(f"Error fetching questions by tag: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching questions by tag: {str(e)}")

@router.get("/questions/tags")
async def get_available_tags():
    """Get all available question tags/categories"""
    try:
        questions = await Question.find_all().to_list()
        tags = list(set(q.tag for q in questions))
        return {"tags": sorted(tags)}
    except Exception as e:
        logging.error(f"Error fetching tags: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching tags: {str(e)}")

@router.post("/questions", response_model=QuestionResponse)
async def create_question(request: QuestionCreate):
    """Manually create a single question"""
    try:
        question = Question(
            question=request.question,
            answer=request.answer,
            question_type=request.question_type,
            options=request.options,
            tag=request.tag
        )
        await question.insert()
        
        return QuestionResponse(
            id=str(question.id),
            question=question.question,
            answer=question.answer,
            question_type=question.question_type,
            options=question.options,
            topic=question.tag,
            tag=question.tag,
            created_at=question.created_at
        )
    except Exception as e:
        logging.error(f"Error creating question: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating question: {str(e)}")

@router.delete("/questions/{question_id}")
async def delete_question(question_id: str):
    """Delete a specific question by ID"""
    try:
        question = await Question.get(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        await question.delete()
        return {"message": "Question deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting question: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting question: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Get statistics about questions in the database"""
    try:
        all_questions = await Question.find_all().to_list()
        
        total_questions = len(all_questions)
        mcq_count = len([q for q in all_questions if q.question_type == "mcq"])
        descriptive_count = len([q for q in all_questions if q.question_type == "descriptive"])
        
        tags = {}
        for q in all_questions:
            tags[q.tag] = tags.get(q.tag, 0) + 1
        
        return {
            "total_questions": total_questions,
            "mcq_questions": mcq_count,
            "descriptive_questions": descriptive_count,
            "questions_by_tag": tags
        }
    except Exception as e:
        logging.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")
