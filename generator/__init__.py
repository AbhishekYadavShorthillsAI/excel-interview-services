"""
Generator Service Package

This package provides AI-powered question generation capabilities with:
- Conversational question generation using Gemini AI
- Direct question generation with specific parameters
- Question management and storage in MongoDB
- Integration with multiple AI services (Gemini, Perplexity)

Main Components:
- models: Database models for questions
- schemas: Pydantic schemas for API validation
- routes: FastAPI endpoints
- handler: Business logic for question generation
- main: FastAPI application entry point
"""

__version__ = "1.0.0"
__author__ = "AI Question Generator"
__description__ = "AI-Powered Question Generation Service" 