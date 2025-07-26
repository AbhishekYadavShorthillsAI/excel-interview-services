import logging
import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from utils.gemini import GeminiClient
from interview.models import (
    InterviewSession, CandidateResponse, InterviewEvaluation,
    EvaluationScore, ResponseType
)

class InterviewEvaluationSystem:
    """
    Simplified evaluation system that evaluates the entire interview at the end:
    - Evaluates all responses comprehensively
    - Calculates performance metrics
    - Generates AI-powered insights and feedback
    - Creates detailed reports
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient(model="gemini-2.0-flash-exp", temperature=0.1)
        self.logger = logging.getLogger(__name__)
    
    async def evaluate_complete_interview(
        self, 
        session: InterviewSession,
        responses: List[CandidateResponse]
    ) -> InterviewEvaluation:
        """
        Comprehensive evaluation of completed interview session
        """
        try:
            self.logger.info(f"Starting evaluation for session {session.id}")
            
            # First, evaluate individual responses using AI
            evaluated_responses = await self._evaluate_all_responses(responses)
            
            # Calculate basic metrics from evaluated responses
            basic_metrics = self._calculate_basic_metrics(evaluated_responses)
            
            # Calculate topic-wise performance
            topic_scores = self._calculate_topic_scores(evaluated_responses)
            
            # Calculate advanced metrics
            advanced_metrics = self._calculate_advanced_metrics(evaluated_responses, session)
            
            # Generate AI insights for the overall interview
            ai_insights = await self._generate_ai_insights(session, evaluated_responses, basic_metrics)
            
            # Create evaluation record
            evaluation = InterviewEvaluation(
                interview_session_id=str(session.id),
                candidate_name=session.candidate_name,
                
                # Basic counts
                total_questions=session.total_questions,
                questions_answered=basic_metrics["questions_answered"],
                questions_skipped=basic_metrics["questions_skipped"],
                
                # Scores
                overall_score=basic_metrics["overall_score"],
                performance_level=self._determine_performance_level(basic_metrics["overall_score"]),
                mcq_score=basic_metrics["mcq_score"],
                descriptive_score=basic_metrics["descriptive_score"],
                topic_scores=topic_scores,
                
                # Advanced metrics
                average_response_time=advanced_metrics["average_response_time"],
                consistency_score=advanced_metrics["consistency_score"],
                communication_quality=advanced_metrics["communication_quality"],
                
                # AI insights
                performance_summary=ai_insights["summary"],
                detailed_analysis=ai_insights["analysis"],
                recommendations=ai_insights["recommendations"],
                
                # Comparison metrics
                percentile_rank=await self._calculate_percentile_rank(basic_metrics["overall_score"])
            )
            
            # Save evaluation
            await evaluation.insert()
            
            # Update individual responses with evaluation results
            await self._update_responses_with_scores(evaluated_responses)
            
            # Update session with final results
            await self._update_session_with_evaluation(session, evaluation)
            
            self.logger.info(f"Evaluation completed for session {session.id}")
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating interview session: {e}")
            raise

    async def _evaluate_all_responses(self, responses: List[CandidateResponse]) -> List[CandidateResponse]:
        """
        Evaluate all responses using AI
        """
        evaluated_responses = []
        
        for response in responses:
            try:
                # Get the question details for context
                evaluation = await self._evaluate_single_response(response)
                
                # Update response with evaluation
                response.score = evaluation["score"]
                response.is_correct = evaluation["is_correct"]
                response.ai_feedback = evaluation["feedback"]
                response.evaluation_notes = evaluation["notes"]
                
                evaluated_responses.append(response)
                
            except Exception as e:
                self.logger.error(f"Error evaluating response {response.id}: {e}")
                # Add fallback scores for failed evaluations
                response.score = 50.0  # Default middle score
                response.is_correct = None
                response.ai_feedback = "Response recorded for review."
                evaluated_responses.append(response)
        
        return evaluated_responses

    async def _evaluate_single_response(self, response: CandidateResponse) -> Dict[str, Any]:
        """
        Evaluate a single response using AI
        """
        evaluation_prompt = f"""
You are evaluating a candidate's response to an interview question. Provide a thorough, fair evaluation.

QUESTION: {response.question_text}
EXPECTED ANSWER: {response.expected_answer}
QUESTION TYPE: {response.question_type}
CANDIDATE'S ANSWER: {response.candidate_answer}

For MCQ questions:
- Check if the answer matches the expected answer
- Score 100 for correct, 0 for incorrect

For descriptive questions:
- Evaluate based on accuracy, completeness, and understanding
- Score on 0-100 scale:
  * 90-100: Excellent (complete, accurate, demonstrates deep understanding)
  * 70-89: Good (mostly correct, minor gaps)
  * 50-69: Average (partially correct, missing key concepts)
  * 0-49: Poor (incorrect or severely incomplete)

Provide your evaluation in this format:
Score: [0-100]
Correct: [true/false for MCQ, null for descriptive]
Feedback: [Constructive feedback explaining the score]
Notes: [Brief evaluation notes]
"""

        try:
            messages = [{"role": "user", "content": evaluation_prompt}]
            response_text, _ = await self.gemini_client.invoke(messages)
            
            # Parse the evaluation response
            return self._parse_evaluation_result(response_text, response)
            
        except Exception as e:
            self.logger.error(f"Error in AI evaluation: {e}")
            return self._create_fallback_evaluation(response)

    def _parse_evaluation_result(self, ai_response: str, response: CandidateResponse) -> Dict[str, Any]:
        """
        Parse AI evaluation response
        """
        try:
            lines = ai_response.strip().split('\n')
            score = None
            is_correct = None
            feedback = ""
            notes = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("Score:"):
                    score_text = line.replace("Score:", "").strip()
                    score = float(score_text)
                elif line.startswith("Correct:"):
                    correct_text = line.replace("Correct:", "").strip().lower()
                    if correct_text in ["true", "false"]:
                        is_correct = correct_text == "true"
                elif line.startswith("Feedback:"):
                    feedback = line.replace("Feedback:", "").strip()
                elif line.startswith("Notes:"):
                    notes = line.replace("Notes:", "").strip()
            
            # Validate score
            if score is None or score < 0 or score > 100:
                score = 50.0
            
            return {
                "score": score,
                "is_correct": is_correct,
                "feedback": feedback or "Response evaluated.",
                "notes": notes or f"AI evaluation completed for {response.question_type} question."
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to parse AI evaluation: {e}")
            return self._create_fallback_evaluation(response)

    def _create_fallback_evaluation(self, response: CandidateResponse) -> Dict[str, Any]:
        """
        Create basic evaluation when AI evaluation fails
        """
        if response.question_type == ResponseType.MCQ:
            # Simple string matching for MCQ
            candidate_answer = response.candidate_answer.strip().lower()
            expected_answer = response.expected_answer.strip().lower()
            is_correct = candidate_answer in expected_answer or expected_answer in candidate_answer
            score = 100.0 if is_correct else 0.0
            
            return {
                "score": score,
                "is_correct": is_correct,
                "feedback": "Correct answer!" if is_correct else "Please review this topic.",
                "notes": "Basic MCQ evaluation"
            }
        else:
            # Basic descriptive evaluation based on response length and presence
            if not response.candidate_answer.strip():
                return {
                    "score": 0.0,
                    "is_correct": None,
                    "feedback": "No answer provided.",
                    "notes": "Empty response"
                }
            
            # Basic scoring based on response length and completeness
            word_count = len(response.candidate_answer.split())
            if word_count >= 30:
                score = 75.0
            elif word_count >= 15:
                score = 60.0
            elif word_count >= 5:
                score = 45.0
            else:
                score = 25.0
            
            return {
                "score": score,
                "is_correct": None,
                "feedback": "Response received and evaluated based on completeness.",
                "notes": "Basic descriptive evaluation"
            }

    def _calculate_basic_metrics(self, responses: List[CandidateResponse]) -> Dict[str, Any]:
        """Calculate basic performance metrics"""
        
        if not responses:
            return {
                "overall_score": 0,
                "mcq_score": None,
                "descriptive_score": None,
                "questions_answered": 0,
                "questions_skipped": 0,
                "accuracy_rate": 0
            }
        
        # Separate MCQ and descriptive responses
        mcq_responses = [r for r in responses if r.question_type == ResponseType.MCQ]
        desc_responses = [r for r in responses if r.question_type == ResponseType.DESCRIPTIVE]
        
        # Calculate scores
        overall_scores = [r.score for r in responses if r.score is not None]
        overall_score = statistics.mean(overall_scores) if overall_scores else 0
        
        mcq_scores = [r.score for r in mcq_responses if r.score is not None]
        mcq_score = statistics.mean(mcq_scores) if mcq_scores else None
        
        desc_scores = [r.score for r in desc_responses if r.score is not None]
        desc_score = statistics.mean(desc_scores) if desc_scores else None
        
        # Count correct answers for accuracy
        correct_responses = [r for r in responses if r.is_correct is True]
        accuracy_rate = len(correct_responses) / len(responses) if responses else 0
        
        # Count answered vs skipped
        answered_count = len([r for r in responses if r.candidate_answer.strip()])
        skipped_count = len(responses) - answered_count
        
        return {
            "overall_score": round(overall_score, 2),
            "mcq_score": round(mcq_score, 2) if mcq_score is not None else None,
            "descriptive_score": round(desc_score, 2) if desc_score is not None else None,
            "questions_answered": answered_count,
            "questions_skipped": skipped_count,
            "accuracy_rate": round(accuracy_rate, 2)
        }

    def _calculate_topic_scores(self, responses: List[CandidateResponse]) -> Dict[str, float]:
        """Calculate performance by topic"""
        topic_scores = {}
        
        # Group responses by topic (we'll extract this from question text or add it to the model)
        for response in responses:
            # For now, use a general topic - this could be enhanced by extracting topic from question
            topic = "general"  # This should ideally come from the question's topic/tag
            
            if topic not in topic_scores:
                topic_scores[topic] = []
            
            if response.score is not None:
                topic_scores[topic].append(response.score)
        
        # Calculate average score per topic
        return {
            topic: round(statistics.mean(scores), 2) if scores else 0
            for topic, scores in topic_scores.items()
        }

    def _calculate_advanced_metrics(
        self, 
        responses: List[CandidateResponse], 
        session: InterviewSession
    ) -> Dict[str, Any]:
        """Calculate advanced performance metrics"""
        
        # Average response time
        response_times = [r.time_spent_seconds for r in responses if r.time_spent_seconds is not None]
        avg_response_time = statistics.mean(response_times) if response_times else None
        
        # Consistency score (how consistent are the scores across questions)
        scores = [r.score for r in responses if r.score is not None]
        consistency_score = None
        if len(scores) > 1:
            score_std = statistics.stdev(scores)
            score_mean = statistics.mean(scores)
            # Lower standard deviation relative to mean = higher consistency
            consistency_score = max(0, 100 - (score_std / score_mean * 100)) if score_mean > 0 else 0
            consistency_score = round(consistency_score, 2)
        
        # Communication quality for descriptive questions
        desc_responses = [r for r in responses if r.question_type == ResponseType.DESCRIPTIVE]
        communication_quality = self._assess_communication_quality(desc_responses)
        
        return {
            "average_response_time": round(avg_response_time, 2) if avg_response_time else None,
            "consistency_score": consistency_score,
            "communication_quality": communication_quality
        }

    def _assess_communication_quality(self, desc_responses: List[CandidateResponse]) -> Optional[float]:
        """Assess communication quality based on descriptive responses"""
        if not desc_responses:
            return None
        
        quality_scores = []
        
        for response in desc_responses:
            answer = response.candidate_answer.strip()
            if not answer:
                quality_scores.append(0)
                continue
            
            # Basic quality indicators
            word_count = len(answer.split())
            sentence_count = len([s for s in answer.split('.') if s.strip()])
            
            # Quality scoring based on structure and length
            if word_count >= 50 and sentence_count >= 3:
                quality_scores.append(90)  # Well-structured, detailed
            elif word_count >= 30 and sentence_count >= 2:
                quality_scores.append(75)  # Good structure
            elif word_count >= 15:
                quality_scores.append(60)  # Adequate
            else:
                quality_scores.append(30)  # Too brief
        
        return round(statistics.mean(quality_scores), 2) if quality_scores else None

    async def _generate_ai_insights(
        self, 
        session: InterviewSession, 
        responses: List[CandidateResponse],
        basic_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations"""
        try:
            # Prepare analysis context
            context = self._prepare_analysis_context(session, responses, basic_metrics)
            
            insights_prompt = f"""
Analyze this interview performance and provide detailed insights:

{context}

Please provide a comprehensive analysis with:
1. A concise performance summary (2-3 sentences)
2. Detailed analysis covering strengths and areas for improvement
3. Specific, actionable recommendations for the candidate

Be constructive, specific, and helpful. Focus on growth opportunities.
"""
            
            messages = [{"role": "user", "content": insights_prompt}]
            response_text, _ = await self.gemini_client.invoke(messages)
            
            # Parse the AI response
            insights = self._parse_ai_insights(response_text)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating AI insights: {e}")
            return self._create_fallback_insights(basic_metrics)

    def _prepare_analysis_context(
        self, 
        session: InterviewSession, 
        responses: List[CandidateResponse],
        metrics: Dict[str, Any]
    ) -> str:
        """Prepare context for AI analysis"""
        
        # Summarize responses
        response_summary = []
        for i, response in enumerate(responses, 1):
            summary = {
                "question_number": i,
                "question_type": response.question_type.value,
                "score": response.score,
                "is_correct": response.is_correct,
                "response_length": len(response.candidate_answer.split()) if response.candidate_answer else 0
            }
            response_summary.append(summary)
        
        context = f"""
INTERVIEW SESSION ANALYSIS
==========================

Candidate: {session.candidate_name}
Topics Assessed: {', '.join(session.topics)}
Difficulty Level: {session.difficulty_level}
Total Questions: {session.total_questions}

PERFORMANCE METRICS:
- Overall Score: {metrics['overall_score']}/100
- Questions Answered: {metrics['questions_answered']} out of {session.total_questions}
- Questions Skipped: {metrics['questions_skipped']}
- Accuracy Rate: {metrics['accuracy_rate']*100:.1f}%
- MCQ Score: {metrics['mcq_score'] or 'N/A'}
- Descriptive Score: {metrics['descriptive_score'] or 'N/A'}

QUESTION-BY-QUESTION PERFORMANCE:
{self._format_response_summary(response_summary)}
"""
        return context

    def _format_response_summary(self, response_summary: List[Dict]) -> str:
        """Format response summary for AI analysis"""
        formatted = []
        for resp in response_summary:
            line = f"Q{resp['question_number']}: {resp['question_type']} | Score: {resp['score'] or 'N/A'} | "
            line += f"Correct: {resp['is_correct'] if resp['is_correct'] is not None else 'N/A'} | "
            line += f"Words: {resp['response_length']}"
            formatted.append(line)
        return "\n".join(formatted)

    def _parse_ai_insights(self, response_text: str) -> Dict[str, Any]:
        """Parse AI insights response"""
        try:
            # Simple parsing - look for section headers
            lines = response_text.split('\n')
            summary = ""
            analysis = ""
            recommendations = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                lower_line = line.lower()
                if "summary" in lower_line or "overview" in lower_line:
                    current_section = "summary"
                elif "analysis" in lower_line or "strengths" in lower_line or "areas" in lower_line:
                    current_section = "analysis"
                elif "recommendation" in lower_line or "suggestion" in lower_line:
                    current_section = "recommendations"
                else:
                    # Add content to current section
                    if current_section == "summary":
                        summary += line + " "
                    elif current_section == "analysis":
                        analysis += line + " "
                    elif current_section == "recommendations":
                        if line.startswith(('-', '*', '1.', '2.', '3.')):
                            recommendations.append(line)
                        else:
                            recommendations.append(line)
            
            # If parsing failed, use the whole response as analysis
            if not summary and not analysis:
                analysis = response_text
                summary = "Performance analysis completed."
            
            # Ensure we have at least basic recommendations
            if not recommendations:
                recommendations = ["Review performance feedback", "Focus on weaker areas", "Continue practicing"]
            
            return {
                "summary": summary.strip() or "Interview performance evaluated.",
                "analysis": analysis.strip() or response_text,
                "recommendations": recommendations[:5]  # Limit to 5 recommendations
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to parse AI insights: {e}")
            return self._create_fallback_insights({})

    def _create_fallback_insights(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback insights when AI analysis fails"""
        overall_score = metrics.get("overall_score", 50)
        
        if overall_score >= 80:
            summary = "Strong performance with solid understanding demonstrated."
            recommendations = ["Continue building expertise", "Explore advanced topics", "Share knowledge with others"]
        elif overall_score >= 60:
            summary = "Good performance with some areas for improvement."
            recommendations = ["Review incorrect answers", "Practice challenging topics", "Focus on clarity"]
        else:
            summary = "Performance shows need for additional study and practice."
            recommendations = ["Review fundamental concepts", "Practice regularly", "Seek additional resources"]
        
        return {
            "summary": summary,
            "analysis": f"Overall score of {overall_score}/100 indicates competency level. Review individual question feedback for specific guidance.",
            "recommendations": recommendations
        }

    async def _calculate_percentile_rank(self, score: float) -> Optional[float]:
        """Calculate percentile rank compared to other candidates"""
        try:
            # Get evaluations from last 3 months for comparison
            three_months_ago = datetime.utcnow() - timedelta(days=90)
            recent_evaluations = await InterviewEvaluation.find(
                InterviewEvaluation.evaluated_at >= three_months_ago
            ).to_list()
            
            if len(recent_evaluations) < 5:  # Need sufficient data
                return None
            
            all_scores = [eval.overall_score for eval in recent_evaluations]
            all_scores.sort()
            
            # Calculate percentile rank
            rank = sum(1 for s in all_scores if s <= score) / len(all_scores)
            return round(rank * 100, 1)
            
        except Exception as e:
            self.logger.error(f"Error calculating percentile rank: {e}")
            return None

    async def _update_responses_with_scores(self, responses: List[CandidateResponse]):
        """Update individual responses with their evaluation scores"""
        try:
            for response in responses:
                await response.save()
            self.logger.info(f"Updated {len(responses)} responses with evaluation scores")
        except Exception as e:
            self.logger.error(f"Error updating responses with scores: {e}")

    async def _update_session_with_evaluation(
        self, 
        session: InterviewSession, 
        evaluation: InterviewEvaluation
    ):
        """Update session with final evaluation results"""
        try:
            session.overall_score = evaluation.overall_score
            session.performance_level = evaluation.performance_level
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            
            # Calculate duration if not already set
            if not session.total_duration_minutes and session.started_at:
                duration = datetime.utcnow() - session.started_at
                session.total_duration_minutes = int(duration.total_seconds() / 60)
            
            await session.save()
            
        except Exception as e:
            self.logger.error(f"Error updating session with evaluation: {e}")

    def _determine_performance_level(self, score: float) -> EvaluationScore:
        """Determine performance level from score"""
        if score >= 90:
            return EvaluationScore.EXCELLENT
        elif score >= 70:
            return EvaluationScore.GOOD
        elif score >= 50:
            return EvaluationScore.AVERAGE
        else:
            return EvaluationScore.POOR

    async def get_evaluation_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get evaluation summary for a session"""
        try:
            evaluation = await InterviewEvaluation.find_one(
                InterviewEvaluation.interview_session_id == session_id
            )
            
            if not evaluation:
                return None
            
            return {
                "session_id": session_id,
                "overall_score": evaluation.overall_score,
                "performance_level": evaluation.performance_level.value,
                "summary": evaluation.performance_summary,
                "recommendations": evaluation.recommendations,
                "percentile_rank": evaluation.percentile_rank
            }
            
        except Exception as e:
            self.logger.error(f"Error getting evaluation summary: {e}")
            return None 