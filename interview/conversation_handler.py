import json
import logging
from typing import List, Dict, Any, Optional
from utils.gemini import GeminiClient
from generator.models import Question
from interview.models import InterviewSession

class ConversationalInterviewHandler:
    """
    Simplified conversational interview handler that:
    - Presents questions naturally using AI
    - Maintains conversation context
    - Handles clarification requests
    - No real-time evaluation (evaluation happens at the end)
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient(model="gemini-2.0-flash-exp", temperature=0.3)
        self.logger = logging.getLogger(__name__)
        
    def _get_interview_system_prompt(self, session: InterviewSession) -> str:
        """Generate system prompt for the interview session"""
        return f"""
You are a professional interviewer conducting an interview for {session.candidate_name}.

INTERVIEW CONTEXT:
- Candidate: {session.candidate_name}
- Topics being assessed: {', '.join(session.topics)}
- Question {session.current_question_index + 1} of {session.total_questions}
- Difficulty level: {session.difficulty_level}

YOUR ROLE:
1. Present questions in a natural, conversational manner
2. Provide clarifications when asked
3. Maintain a professional yet friendly tone
4. Guide the candidate through the interview process
5. Do NOT evaluate answers - just acknowledge them and move forward

GUIDELINES:
- Be encouraging and supportive
- Keep responses concise and clear
- Ask follow-up questions for clarification if needed
- Do not provide hints or reveal correct answers
- Focus on smooth conversation flow

IMPORTANT: You are NOT evaluating answers during the interview. Just present questions, accept answers, and maintain good conversation flow.
"""

    async def present_question(
        self, 
        session: InterviewSession, 
        question: Question
    ) -> Dict[str, Any]:
        """
        Present a question to the candidate in a conversational manner
        """
        try:
            # Build conversation context
            messages = self._build_conversation_context(session)
            
            # Create question presentation prompt
            question_prompt = self._format_question_presentation(question, session)
            messages.append({
                "role": "user",
                "content": question_prompt
            })
            
            # Get AI response for question presentation
            response_text, updated_messages = await self.gemini_client.invoke(messages)
            
            # Update session conversation history
            await self._update_conversation_history(session, updated_messages[-2:])
            
            return {
                "success": True,
                "presentation": response_text,
                "question_id": str(question.id),
                "question_type": question.question_type
            }
            
        except Exception as e:
            self.logger.error(f"Error presenting question: {e}")
            return {
                "success": False,
                "error": str(e),
                "presentation": self._create_fallback_presentation(question, session)
            }

    async def acknowledge_answer(
        self,
        session: InterviewSession,
        question: Question,
        candidate_answer: str
    ) -> Dict[str, Any]:
        """
        Acknowledge the candidate's answer without evaluation
        """
        try:
            # Build conversation context
            messages = self._build_conversation_context(session)
            
            # Create acknowledgment prompt
            acknowledgment_prompt = f"""
The candidate has provided their answer to the current question.

Question: {question.question}
Candidate's answer: {candidate_answer}

Please acknowledge their response in a professional, encouraging way. Do NOT evaluate or judge the answer. Just:
1. Thank them for their response
2. Provide brief encouraging feedback
3. Let them know you're ready to move to the next question (if there are more)

Keep it brief and positive.
"""
            messages.append({
                "role": "user",
                "content": acknowledgment_prompt
            })
            
            # Get AI acknowledgment
            response_text, updated_messages = await self.gemini_client.invoke(messages)
            
            # Update conversation history
            await self._update_conversation_history(session, updated_messages[-2:])
            
            return {
                "success": True,
                "acknowledgment": response_text
            }
            
        except Exception as e:
            self.logger.error(f"Error acknowledging answer: {e}")
            return {
                "success": False,
                "error": str(e),
                "acknowledgment": "Thank you for your answer. Let's continue with the next question."
            }

    async def handle_clarification_request(
        self,
        session: InterviewSession,
        candidate_message: str
    ) -> Dict[str, Any]:
        """
        Handle candidate's request for clarification
        """
        try:
            messages = self._build_conversation_context(session)
            
            clarification_prompt = f"""
The candidate is asking for clarification or has a question:

Candidate's message: "{candidate_message}"

Please provide a helpful response that:
1. Addresses their question clearly
2. Provides necessary clarification without giving away answers
3. Encourages them to think through the problem
4. Maintains the interview flow

Be supportive and professional.
"""
            messages.append({
                "role": "user",
                "content": clarification_prompt
            })
            
            response_text, updated_messages = await self.gemini_client.invoke(messages)
            
            # Update conversation history
            await self._update_conversation_history(session, updated_messages[-2:])
            
            return {
                "success": True,
                "response": response_text
            }
            
        except Exception as e:
            self.logger.error(f"Error handling clarification: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I understand you need clarification. Could you please rephrase your question?"
            }

    async def generate_interview_transition(
        self,
        session: InterviewSession
    ) -> str:
        """
        Generate natural transitions between questions
        """
        try:
            messages = [{
                "role": "system",
                "content": self._get_interview_system_prompt(session)
            }]
            
            transition_prompt = f"""
Generate a brief, natural transition to the next question.

Current progress: Question {session.current_question_index + 1} of {session.total_questions}

Create a smooth transition that:
1. Acknowledges their progress
2. Prepares them for the next question
3. Maintains positive energy
4. Is 1-2 sentences maximum

Be encouraging and professional.
"""
            
            messages.append({
                "role": "user",
                "content": transition_prompt
            })
            
            response_text, _ = await self.gemini_client.invoke(messages)
            return response_text.strip('"')
            
        except Exception as e:
            self.logger.error(f"Error generating transition: {e}")
            return f"Great! Let's move on to question {session.current_question_index + 2}."

    def _build_conversation_context(self, session: InterviewSession) -> List[Dict[str, str]]:
        """Build conversation context from session history"""
        messages = [{
            "role": "system",
            "content": self._get_interview_system_prompt(session)
        }]
        
        # Add recent conversation history (last 8 exchanges to keep context manageable)
        recent_history = session.conversation_history[-8:] if len(session.conversation_history) > 8 else session.conversation_history
        
        for exchange in recent_history:
            if exchange.get("role") and exchange.get("content"):
                messages.append({
                    "role": exchange["role"],
                    "content": exchange["content"]
                })
        
        return messages

    def _format_question_presentation(self, question: Question, session: InterviewSession) -> str:
        """Format question for natural presentation"""
        question_info = {
            "question_text": question.question,
            "question_type": question.question_type,
            "options": question.options if question.question_type == "mcq" else None,
            "topic": question.tag,
            "question_number": session.current_question_index + 1,
            "total_questions": session.total_questions
        }
        
        return f"""
Please present this question to the candidate in a natural, conversational way:

{json.dumps(question_info, indent=2)}

Instructions:
1. Present the question clearly and professionally  
2. If it's an MCQ, present the options in a clear format
3. Provide context about what kind of response you're looking for
4. End with a clear invitation for them to respond
5. Keep it conversational and encouraging

Remember: You are not evaluating their answer - just presenting the question.
"""

    def _create_fallback_presentation(self, question: Question, session: InterviewSession) -> str:
        """Create a basic question presentation when AI fails"""
        question_num = session.current_question_index + 1
        
        presentation = f"Question {question_num} of {session.total_questions}:\n\n{question.question}"
        
        if question.question_type == "mcq" and question.options:
            presentation += "\n\nOptions:\n"
            for i, option in enumerate(question.options, 1):
                presentation += f"{chr(64+i)}. {option}\n"
            presentation += "\nPlease select the best answer."
        else:
            presentation += "\n\nPlease provide your answer with as much detail as you think is appropriate."
        
        return presentation

    async def _update_conversation_history(
        self, 
        session: InterviewSession, 
        new_messages: List[Dict[str, str]]
    ):
        """Update session conversation history"""
        try:
            session.conversation_history.extend(new_messages)
            
            # Keep conversation history manageable (last 20 exchanges)
            if len(session.conversation_history) > 20:
                session.conversation_history = session.conversation_history[-20:]
            
            await session.save()
            
        except Exception as e:
            self.logger.error(f"Error updating conversation history: {e}")

    async def generate_interview_completion_message(self, session: InterviewSession) -> str:
        """Generate a completion message when interview ends"""
        try:
            messages = [{
                "role": "system", 
                "content": self._get_interview_system_prompt(session)
            }]
            
            completion_prompt = f"""
The interview has been completed! The candidate {session.candidate_name} has answered all {session.total_questions} questions.

Generate a professional, encouraging completion message that:
1. Congratulates them on completing the interview
2. Thanks them for their time and effort  
3. Explains that their responses will be evaluated
4. Sets expectations for when they might hear back
5. Ends on a positive, professional note

Keep it warm but professional, around 2-3 sentences.
"""
            
            messages.append({"role": "user", "content": completion_prompt})
            
            response_text, _ = await self.gemini_client.invoke(messages)
            return response_text.strip('"')
            
        except Exception as e:
            self.logger.error(f"Error generating completion message: {e}")
            return f"Congratulations {session.candidate_name}! You've completed all {session.total_questions} questions. Your responses will be evaluated and you'll receive feedback soon. Thank you for your time!" 