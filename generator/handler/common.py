from generator.models import Question
from typing import List, Optional
import logging

async def save_questions_to_db(questions: List[dict]):
    """Save a list of question dictionaries to the database"""
    try:
        docs = [Question(**q) for q in questions]
        await Question.insert_many(docs)
        logging.info(f"Successfully saved {len(docs)} questions to database")
        return True
    except Exception as e:
        logging.error(f"Error saving questions to database: {e}")
        return False

async def fetch_questions_by_tag(tag: Optional[str] = None):
    """Fetch questions, optionally filtered by tag"""
    try:
        if tag:
            questions = await Question.find(Question.tag == tag).to_list()
        else:
            questions = await Question.find_all().to_list()
        return sorted(questions, key=lambda x: x.tag)
    except Exception as e:
        logging.error(f"Error fetching questions: {e}")
        return []
