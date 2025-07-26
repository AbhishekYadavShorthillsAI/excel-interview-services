# AI Interview Service

An intelligent, conversational interview system that uses AI to conduct interviews, evaluate responses, and provide comprehensive performance analysis.

## Features

### 🤖 Conversational AI Interviews
- Natural, conversational interview experience using Gemini AI
- Adaptive questioning based on candidate responses
- Real-time clarification and follow-up questions
- Context-aware conversation flow

### 🧠 Intelligent Question Selection
- Smart selection from existing question pools
- Balanced topic coverage and question type distribution  
- Difficulty-based filtering (easy, medium, hard, mixed, adaptive)
- Exclusion capabilities to avoid duplicate questions

### 📊 Advanced Evaluation System
- AI-powered response evaluation for both MCQ and descriptive questions
- Multi-dimensional scoring (accuracy, completeness, communication quality)
- Performance trend analysis and consistency scoring
- Comparative analysis with historical data

### 📈 Comprehensive Analytics
- Detailed performance reports with AI-generated insights
- Topic-wise performance breakdown
- Time-based metrics and efficiency analysis  
- Percentile ranking against other candidates
- Actionable recommendations for improvement

## Architecture

```
interview/
├── models.py              # Database models (InterviewSession, CandidateResponse, etc.)
├── schemas.py             # API request/response schemas
├── question_selector.py   # Intelligent question selection logic
├── conversation_handler.py # AI conversational interview management
├── evaluation_system.py   # Performance evaluation and analysis
├── routes.py             # FastAPI endpoints
├── main.py               # Application entry point
└── README.md             # This file
```

## Core Components

### 1. Question Selector (`question_selector.py`)
- **Mixed Difficulty**: Balanced selection across topics and question types
- **Adaptive Mode**: Progressive difficulty based on performance
- **Fixed Difficulty**: Consistent difficulty level throughout
- **Topic Distribution**: Ensures even coverage of specified topics

### 2. Conversation Handler (`conversation_handler.py`)
- **Question Presentation**: Natural, contextual question delivery
- **Response Evaluation**: AI-powered assessment of candidate answers
- **Clarification Support**: Handles candidate questions and requests
- **Conversation Flow**: Maintains interview context and progression

### 3. Evaluation System (`evaluation_system.py`)
- **Performance Metrics**: Overall scores, accuracy rates, consistency
- **Topic Analysis**: Performance breakdown by subject area
- **AI Insights**: Generated summaries and recommendations
- **Comparative Analysis**: Percentile ranking and benchmarking

## API Endpoints

### Interview Management
- `POST /api/v1/interview/start` - Start new interview session
- `GET /api/v1/interview/session/{id}/question` - Get current question
- `POST /api/v1/interview/session/{id}/answer` - Submit answer
- `POST /api/v1/interview/session/{id}/conversation` - Continue conversation

### Evaluation & Reporting  
- `GET /api/v1/interview/session/{id}/evaluation` - Get evaluation results
- `GET /api/v1/interview/session/{id}/history` - Get interview history
- `GET /api/v1/interview/session/{id}/report` - Generate performance report

### Administration
- `GET /api/v1/interview/sessions` - List all sessions
- `GET /api/v1/interview/stats` - Get system statistics
- `POST /api/v1/interview/questions/select` - Preview question selection

## Usage Examples

### Starting an Interview
```bash
curl -X POST "http://localhost:8001/api/v1/interview/start" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "John Doe",
    "candidate_email": "john@example.com",
    "topics": ["Excel Formulas", "VBA"],
    "total_questions": 10,
    "difficulty_level": "mixed"
  }'
```

### Getting a Question
```bash
curl "http://localhost:8001/api/v1/interview/session/{session_id}/question"
```

### Submitting an Answer
```bash
curl -X POST "http://localhost:8001/api/v1/interview/session/{session_id}/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "{session_id}",
    "answer": "VLOOKUP is used to search for values...",
    "selected_option": "A",
    "time_spent_seconds": 45
  }'
```

### Getting Evaluation Results
```bash
curl "http://localhost:8001/api/v1/interview/session/{session_id}/evaluation"
```

## Configuration

The service uses environment variables for configuration:

```env
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=excel_interviewer

# AI Service
GEMINI_API_KEY=your_gemini_api_key

# Service Configuration  
HOST=0.0.0.0
PORT=8001
DEBUG=false
```

## Running the Service

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGODB_URI="mongodb://localhost:27017" 
export GEMINI_API_KEY="your_api_key"

# Run the service
python -m interview.main
```

### Production
```bash
# Using uvicorn directly
uvicorn interview.main:app --host 0.0.0.0 --port 8001 --workers 4

# Or using Docker (if Dockerfile provided)
docker build -t interview-service .
docker run -p 8001:8001 interview-service
```

## Integration with Generator Service

This interview service depends on questions created by the generator service:

1. **Question Pool**: Retrieves questions from MongoDB collections created by generator
2. **Topic Selection**: Uses tags/categories from generator service
3. **Question Structure**: Compatible with MCQ and descriptive question formats

Make sure the generator service has created questions before running interviews.

## Performance Considerations

- **Database Optimization**: Indexes on session_id, candidate responses, and evaluation queries
- **AI Rate Limits**: Configured with appropriate request limits for Gemini API
- **Background Processing**: Evaluation tasks run asynchronously to avoid blocking
- **Caching**: Conversation history limited to prevent memory issues

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **Structured Logging**: JSON-formatted logs for better analysis
- **Error Tracking**: Comprehensive error handling with detailed logging
- **Performance Metrics**: Response times and AI processing duration

## Future Enhancements

- **Multi-language Support**: Interview localization capabilities
- **Video/Audio Integration**: Support for multimedia interview components
- **Advanced Analytics**: Machine learning-based performance prediction
- **Integration APIs**: Webhooks for external systems
- **Mobile Optimization**: Enhanced mobile interview experience

---

For more information, see the API documentation at `/docs` when running the service. 