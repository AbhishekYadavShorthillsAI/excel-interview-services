from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime

from interview.schemas import (
    StartInterviewRequest, InterviewSessionResponse, SubmitAnswerRequest,
    SubmitAnswerResponse, QuestionResponse, ContinueConversationRequest,
    ConversationResponse, InterviewEvaluationResponse, InterviewSummaryResponse,
    InterviewStatsResponse, QuestionSelectionRequest, QuestionSelectionResponse
)

from interview.models import (
    InterviewSession, CandidateResponse, InterviewEvaluation, 
    InterviewStatus, ResponseType
)

from interview.question_selector import IntelligentQuestionSelector
from interview.conversation_handler import ConversationalInterviewHandler
from interview.evaluation_system import InterviewEvaluationSystem
from generator.models import Question

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize core components
question_selector = IntelligentQuestionSelector()
conversation_handler = ConversationalInterviewHandler()
evaluation_system = InterviewEvaluationSystem()

@router.post("/start", response_model=InterviewSessionResponse)
async def start_interview(request: StartInterviewRequest):
    """
    Start a new interview session
    """
    try:
        logger.info(f"Starting interview for {request.candidate_name}")
        
        # Select questions for the interview
        selected_questions, strategy = await question_selector.select_questions_for_interview(
            topics=request.topics,
            total_questions=request.total_questions,
            difficulty_level=request.difficulty_level
        )
        
        # Create interview session
        session = InterviewSession(
            candidate_name=request.candidate_name,
            candidate_email=request.candidate_email,
            topics=request.topics,
            total_questions=request.total_questions,
            difficulty_level=request.difficulty_level,
            status=InterviewStatus.ACTIVE,
            current_question_index=0,
            questions_asked=[str(q.id) for q in selected_questions],
            conversation_history=[]
        )
        
        await session.insert()
        logger.info(f"Created interview session {session.id} with {len(selected_questions)} questions")
        
        return InterviewSessionResponse(
            session_id=str(session.id),
            candidate_name=session.candidate_name,
            candidate_email=session.candidate_email,
            topics=session.topics,
            total_questions=session.total_questions,
            difficulty_level=session.difficulty_level,
            status=session.status,
            current_question_index=session.current_question_index,
            started_at=session.started_at
        )
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/question", response_model=QuestionResponse)
async def get_current_question(session_id: str):
    """
    Get the current question for an interview session
    """
    try:
        # Get session
        session = await InterviewSession.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # Check if interview is completed
        if session.current_question_index >= len(session.questions_asked):
            raise HTTPException(status_code=400, detail="Interview completed")
        
        # Get current question
        question_id = session.questions_asked[session.current_question_index]
        question = await Question.get(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Present question using conversation handler
        presentation_result = await conversation_handler.present_question(session, question)
        
        if not presentation_result["success"]:
            # Fallback presentation
            context = f"Question {session.current_question_index + 1} of {session.total_questions}"
        else:
            context = presentation_result["presentation"]
        
        return QuestionResponse(
            question_id=str(question.id),
            question_text=question.question,
            question_type=ResponseType(question.question_type),
            options=question.options if question.question_type == "mcq" else None,
            context=context,
            question_number=session.current_question_index + 1,
            total_questions=session.total_questions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/{session_id}/answer", response_model=SubmitAnswerResponse)
async def submit_answer(session_id: str, request: SubmitAnswerRequest):
    """
    Submit an answer for the current question
    """
    try:
        # Get session
        session = await InterviewSession.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # Check if interview is completed
        if session.current_question_index >= len(session.questions_asked):
            raise HTTPException(status_code=400, detail="Interview already completed")
        
        # Get current question
        question_id = session.questions_asked[session.current_question_index]
        question = await Question.get(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Save candidate response (without evaluation - that happens at the end)
        response = CandidateResponse(
            interview_session_id=session_id,
            question_id=str(question.id),
            question_text=question.question,
            question_type=ResponseType(question.question_type),
            candidate_answer=request.answer,
            expected_answer=question.answer,
            options=question.options if question.question_type == "mcq" else None,
            selected_option=request.selected_option,
            time_spent_seconds=request.time_spent_seconds,
            answered_at=datetime.utcnow()
        )
        
        await response.insert()
        
        # Acknowledge answer using conversation handler
        acknowledgment_result = await conversation_handler.acknowledge_answer(
            session, question, request.answer
        )
        
        acknowledgment = acknowledgment_result.get("acknowledgment", "Thank you for your answer.")
        
        # Move to next question
        session.current_question_index += 1
        await session.save()
        
        # Check if interview is completed
        is_interview_complete = session.current_question_index >= len(session.questions_asked)
        
        next_question = None
        if not is_interview_complete:
            # Get next question
            try:
                next_question_id = session.questions_asked[session.current_question_index]
                next_q = await Question.get(next_question_id)
                
                if next_q:
                    next_question = QuestionResponse(
                        question_id=str(next_q.id),
                        question_text=next_q.question,
                        question_type=ResponseType(next_q.question_type),
                        options=next_q.options if next_q.question_type == "mcq" else None,
                        context=f"Question {session.current_question_index + 1} of {session.total_questions}",
                        question_number=session.current_question_index + 1,
                        total_questions=session.total_questions
                    )
            except Exception as e:
                logger.warning(f"Error preparing next question: {e}")
        
        # If interview is complete, trigger evaluation
        if is_interview_complete:
            try:
                # Get all responses for evaluation
                all_responses = await CandidateResponse.find(
                    CandidateResponse.interview_session_id == session_id
                ).to_list()
                
                # Trigger end-of-interview evaluation
                await evaluation_system.evaluate_complete_interview(session, all_responses)
                
                # Generate completion message
                completion_message = await conversation_handler.generate_interview_completion_message(session)
                acknowledgment = completion_message
                
            except Exception as e:
                logger.error(f"Error during interview completion: {e}")
                acknowledgment = f"Congratulations {session.candidate_name}! You've completed the interview. Your responses will be evaluated soon."
        
        return SubmitAnswerResponse(
            success=True,
            message=acknowledgment,
            feedback=None,  # No real-time feedback
            next_question=next_question,
            is_interview_complete=is_interview_complete
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/{session_id}/conversation", response_model=ConversationResponse)
async def continue_conversation(session_id: str, request: ContinueConversationRequest):
    """
    Handle clarification requests or continue conversation
    """
    try:
        # Get session
        session = await InterviewSession.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # Handle clarification request
        clarification_result = await conversation_handler.handle_clarification_request(
            session, request.message
        )
        
        if not clarification_result["success"]:
            response_text = "I understand you need clarification. Could you please rephrase your question?"
        else:
            response_text = clarification_result["response"]
        
        return ConversationResponse(
            response=response_text,
            next_question=None,  # Clarification doesn't advance the interview
            is_clarification_needed=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/evaluation", response_model=InterviewEvaluationResponse)
async def get_evaluation(session_id: str):
    """
    Get evaluation results for a completed interview
    """
    try:
        # Check if session exists and is completed
        session = await InterviewSession.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        if session.status != InterviewStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Interview not yet completed")
        
        # Get evaluation
        evaluation = await InterviewEvaluation.find_one(
            InterviewEvaluation.interview_session_id == session_id
        )
        
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        return InterviewEvaluationResponse(
            session_id=session_id,
            candidate_name=evaluation.candidate_name,
            overall_score=evaluation.overall_score,
            performance_level=evaluation.performance_level,
            total_questions=evaluation.total_questions,
            questions_answered=evaluation.questions_answered,
            questions_skipped=evaluation.questions_skipped,
            mcq_score=evaluation.mcq_score,
            descriptive_score=evaluation.descriptive_score,
            topic_scores=evaluation.topic_scores,
            average_response_time=evaluation.average_response_time,
            consistency_score=evaluation.consistency_score,
            communication_quality=evaluation.communication_quality,
            performance_summary=evaluation.performance_summary,
            detailed_analysis=evaluation.detailed_analysis,
            strengths=[],  # Can be derived from analysis
            areas_for_improvement=[],  # Can be derived from analysis
            recommendations=evaluation.recommendations,
            interview_duration_minutes=session.total_duration_minutes,
            completed_at=session.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[InterviewSummaryResponse])
async def list_sessions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None)
):
    """
    List interview sessions
    """
    try:
        # Build query
        query = {}
        if status:
            try:
                query["status"] = InterviewStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status")
        
        # Get sessions
        sessions = await InterviewSession.find(query).skip(offset).limit(limit).to_list()
        
        result = []
        for session in sessions:
            result.append(InterviewSummaryResponse(
                session_id=str(session.id),
                candidate_name=session.candidate_name,
                status=session.status,
                overall_score=session.overall_score,
                performance_level=session.performance_level,
                questions_answered=session.current_question_index,
                total_questions=session.total_questions,
                started_at=session.started_at,
                completed_at=session.completed_at
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=InterviewStatsResponse)
async def get_interview_stats():
    """
    Get interview service statistics
    """
    try:
        # Count sessions by status
        total_interviews = await InterviewSession.count()
        active_interviews = await InterviewSession.find(
            InterviewSession.status == InterviewStatus.ACTIVE
        ).count()
        completed_interviews = await InterviewSession.find(
            InterviewSession.status == InterviewStatus.COMPLETED
        ).count()
        
        # Calculate average score from completed evaluations
        evaluations = await InterviewEvaluation.find_all().to_list()
        average_score = sum(e.overall_score for e in evaluations) / len(evaluations) if evaluations else 0
        
        # Score distribution
        score_distribution = {"excellent": 0, "good": 0, "average": 0, "poor": 0}
        for evaluation in evaluations:
            if evaluation.performance_level:
                score_distribution[evaluation.performance_level.value] += 1
        
        # Popular topics (simplified)
        popular_topics = {}
        sessions = await InterviewSession.find_all().to_list()
        for session in sessions:
            for topic in session.topics:
                popular_topics[topic] = popular_topics.get(topic, 0) + 1
        
        return InterviewStatsResponse(
            total_interviews=total_interviews,
            active_interviews=active_interviews,
            completed_interviews=completed_interviews,
            average_score=round(average_score, 2),
            score_distribution=score_distribution,
            popular_topics=popular_topics
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/questions/preview", response_model=QuestionSelectionResponse)
async def preview_question_selection(request: QuestionSelectionRequest):
    """
    Preview question selection without starting an interview
    """
    try:
        # Get question statistics
        stats = await question_selector.get_question_statistics(request.topics)
        
        # Select questions (without creating a session)
        selected_questions, strategy = await question_selector.select_questions_for_interview(
            topics=request.topics,
            total_questions=request.count,
            difficulty_level=request.difficulty_level
        )
        
        # Format questions for response
        questions_info = []
        for q in selected_questions:
            questions_info.append({
                "id": str(q.id),
                "question": q.question,
                "type": q.question_type,
                "topic": q.tag,
                "options": q.options if q.question_type == "mcq" else None
            })
        
        return QuestionSelectionResponse(
            questions=questions_info,
            selection_strategy=strategy,
            total_available=stats["total_questions"]
        )
        
    except Exception as e:
        logger.error(f"Error previewing questions: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 