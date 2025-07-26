import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from generator.models import Question
from interview.models import InterviewSession

class IntelligentQuestionSelector:
    """
    Simplified intelligent question selection system that:
    - Selects questions based on topics
    - Provides basic difficulty distribution
    - Balances MCQ and descriptive questions
    - Uses random selection within constraints
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def select_questions_for_interview(
        self,
        topics: List[str],
        total_questions: int,
        difficulty_level: str = "mixed"
    ) -> Tuple[List[Question], str]:
        """
        Select questions for a new interview session
        
        Args:
            topics: List of topics to select questions from
            total_questions: Number of questions to select
            difficulty_level: "easy", "medium", "hard", or "mixed"
            
        Returns:
            Tuple of (selected_questions, selection_strategy)
        """
        try:
            # Get all available questions for the topics
            all_questions = await self._fetch_questions_by_topics(topics)
            
            if len(all_questions) < total_questions:
                raise ValueError(
                    f"Not enough questions available. Found {len(all_questions)}, need {total_questions}"
                )
            
            # Select questions based on difficulty level
            if difficulty_level == "mixed":
                selected_questions = await self._select_mixed_questions(all_questions, total_questions)
                strategy = f"Mixed difficulty with balanced topic coverage"
            else:
                selected_questions = await self._select_by_difficulty(
                    all_questions, total_questions, difficulty_level
                )
                strategy = f"Fixed difficulty level: {difficulty_level}"
            
            # Shuffle to randomize order
            random.shuffle(selected_questions)
            
            self.logger.info(f"Selected {len(selected_questions)} questions using strategy: {strategy}")
            return selected_questions, strategy
            
        except Exception as e:
            self.logger.error(f"Error selecting questions: {e}")
            raise

    async def _fetch_questions_by_topics(self, topics: List[str]) -> List[Question]:
        """Fetch all questions matching the given topics"""
        try:
            questions = []
            for topic in topics:
                topic_questions = await Question.find(Question.tag == topic).to_list()
                questions.extend(topic_questions)
            
            # Remove duplicates
            seen = set()
            unique_questions = []
            for q in questions:
                if q.id not in seen:
                    seen.add(q.id)
                    unique_questions.append(q)
            
            self.logger.info(f"Found {len(unique_questions)} questions for topics: {topics}")
            return unique_questions
            
        except Exception as e:
            self.logger.error(f"Error fetching questions for topics {topics}: {e}")
            return []

    async def _select_mixed_questions(
        self, 
        questions: List[Question], 
        total_questions: int
    ) -> List[Question]:
        """
        Select questions with mixed difficulty - balance MCQ and descriptive
        """
        # Separate question types
        mcq_questions = [q for q in questions if q.question_type == "mcq"]
        desc_questions = [q for q in questions if q.question_type == "descriptive"]
        
        # Aim for 60% MCQ, 40% descriptive (but adjust if not enough of either type)
        target_mcq = int(total_questions * 0.6)
        target_desc = total_questions - target_mcq
        
        # Adjust if we don't have enough of either type
        available_mcq = min(len(mcq_questions), target_mcq)
        available_desc = min(len(desc_questions), target_desc)
        
        # If we need more questions, use what's available
        if available_mcq + available_desc < total_questions:
            remaining_needed = total_questions - available_mcq - available_desc
            if len(mcq_questions) > available_mcq:
                available_mcq = min(len(mcq_questions), available_mcq + remaining_needed)
            elif len(desc_questions) > available_desc:
                available_desc = min(len(desc_questions), available_desc + remaining_needed)
        
        # Randomly select from each type
        selected_questions = []
        if available_mcq > 0:
            selected_questions.extend(random.sample(mcq_questions, available_mcq))
        if available_desc > 0:
            selected_questions.extend(random.sample(desc_questions, available_desc))
        
        return selected_questions[:total_questions]

    async def _select_by_difficulty(
        self, 
        questions: List[Question], 
        total_questions: int, 
        difficulty: str
    ) -> List[Question]:
        """
        Select questions by difficulty level
        Since we don't have explicit difficulty ratings, we use question type as proxy:
        - easy: prefer MCQ questions
        - medium: balanced mix
        - hard: prefer descriptive questions
        """
        if difficulty == "easy":
            # Prefer MCQ questions for easy level
            mcq_questions = [q for q in questions if q.question_type == "mcq"]
            desc_questions = [q for q in questions if q.question_type == "descriptive"]
            
            if len(mcq_questions) >= total_questions:
                return random.sample(mcq_questions, total_questions)
            else:
                # Use all MCQ and supplement with descriptive
                selected = mcq_questions[:]
                remaining = total_questions - len(selected)
                if remaining > 0 and desc_questions:
                    selected.extend(random.sample(desc_questions, min(remaining, len(desc_questions))))
                return selected[:total_questions]
                
        elif difficulty == "hard":
            # Prefer descriptive questions for hard level
            desc_questions = [q for q in questions if q.question_type == "descriptive"]
            mcq_questions = [q for q in questions if q.question_type == "mcq"]
            
            if len(desc_questions) >= total_questions:
                return random.sample(desc_questions, total_questions)
            else:
                # Use all descriptive and supplement with MCQ
                selected = desc_questions[:]
                remaining = total_questions - len(selected)
                if remaining > 0 and mcq_questions:
                    selected.extend(random.sample(mcq_questions, min(remaining, len(mcq_questions))))
                return selected[:total_questions]
                
        else:  # medium - balanced mix
            return await self._select_mixed_questions(questions, total_questions)

    async def get_question_statistics(self, topics: List[str]) -> Dict[str, Any]:
        """Get basic statistics about available questions for given topics"""
        questions = await self._fetch_questions_by_topics(topics)
        
        mcq_count = len([q for q in questions if q.question_type == "mcq"])
        desc_count = len([q for q in questions if q.question_type == "descriptive"])
        
        # Count by topic
        topic_counts = {}
        for question in questions:
            topic = question.tag
            if topic not in topic_counts:
                topic_counts[topic] = {"mcq": 0, "descriptive": 0}
            topic_counts[topic][question.question_type] += 1
        
        return {
            "total_questions": len(questions),
            "mcq_questions": mcq_count,
            "descriptive_questions": desc_count,
            "by_topic": topic_counts,
            "topics_available": list(topic_counts.keys())
        } 