"""
AI Interview Service Package

This package provides intelligent, conversational interview capabilities with:
- Smart question selection from MongoDB question pools
- Real-time AI-powered evaluation of candidate responses
- Conversational interview experience using Gemini AI
- Comprehensive performance analysis and reporting
- Adaptive difficulty based on candidate performance

Main Components:
- models: Database models for interviews, responses, and evaluations
- schemas: Pydantic schemas for API validation
- question_selector: Intelligent question selection algorithms
- conversation_handler: AI-powered conversational interview management
- evaluation_system: Comprehensive performance evaluation and analysis
- routes: FastAPI endpoints for the interview service
- main: FastAPI application entry point

Usage:
    Start the interview service:
    python -m interview.main
    
    Or use uvicorn directly:
    uvicorn interview.main:app --host 0.0.0.0 --port 8001
"""

__version__ = "1.0.0"
__author__ = "AI Interview System"
__description__ = "Intelligent Conversational Interview Service" 