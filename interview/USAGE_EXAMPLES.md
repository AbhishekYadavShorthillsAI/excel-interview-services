# Interview Service - Usage Examples

Quick examples and common usage patterns for the AI Interview Service Streamlit UI.

## 🚀 Quick Start

### 1. One-Command Startup
```bash
# From project root
./interview/start_ui.sh
```

### 2. Manual Startup
```bash
# Install dependencies
pip install -r interview/streamlit_requirements.txt

# Start the UI
python interview/run_streamlit.py
```

### 3. Direct Streamlit
```bash
streamlit run interview/streamlit_app.py --server.port 8502
```

## 📋 Complete Workflow Example

### Step 1: Start Services
```bash
# Terminal 1: Start Interview Service
cd interview/
python main.py

# Terminal 2: Start Streamlit UI
./interview/start_ui.sh
```

### Step 2: Create Your First Interview
1. **Navigate to UI**: http://localhost:8502
2. **Go to "🚀 Start Interview"**
3. **Fill candidate details**:
   - Name: "John Doe"
   - Email: "john@example.com"
   - Topics: ["Excel Formulas", "VBA Programming"]
   - Questions: 10
   - Difficulty: "mixed"
4. **Click "Start Interview"**

### Step 3: Conduct Interview
1. **Switch to "💬 Take Interview"**
2. **Select the active session**
3. **Present questions to candidate**
4. **Submit answers and get feedback**
5. **Continue until completion**

### Step 4: Review Results
1. **Go to "📊 View Results"**
2. **Enter session ID or select from list**
3. **Review comprehensive evaluation**
4. **Export or share results**

## 🎯 Common Use Cases

### Interview Session Management

#### Starting Multiple Interviews
```python
# Via API (for automation)
import requests

candidates = [
    {"name": "Alice Smith", "email": "alice@company.com", "topics": ["Excel Formulas"]},
    {"name": "Bob Johnson", "email": "bob@company.com", "topics": ["VBA Programming"]},
]

for candidate in candidates:
    response = requests.post("http://localhost:8001/api/v1/interview/start", json={
        "candidate_name": candidate["name"],
        "candidate_email": candidate["email"],
        "topics": candidate["topics"],
        "total_questions": 15,
        "difficulty_level": "mixed"
    })
    print(f"Started interview for {candidate['name']}: {response.json()['session_id']}")
```

#### Batch Session Monitoring
1. **Go to "⚙️ Session Management"**
2. **Filter by status** (active/completed)
3. **Monitor progress** for all sessions
4. **Take bulk actions** as needed

### Analytics and Reporting

#### Performance Dashboard
1. **Access "📈 Analytics Dashboard"**
2. **View key metrics**:
   - Total interviews conducted
   - Average scores by topic
   - Performance distribution
   - Popular interview topics

#### Custom Reports
```python
# Generate custom analytics
def generate_team_report(sessions):
    """Example: Generate team performance report"""
    total_sessions = len(sessions)
    avg_score = sum(s.get('overall_score', 0) for s in sessions) / total_sessions
    
    topic_performance = {}
    for session in sessions:
        for topic in session.get('topics', []):
            if topic not in topic_performance:
                topic_performance[topic] = []
            topic_performance[topic].append(session.get('overall_score', 0))
    
    return {
        "team_size": total_sessions,
        "average_score": avg_score,
        "topic_averages": {
            topic: sum(scores) / len(scores) 
            for topic, scores in topic_performance.items()
        }
    }
```

## 🔧 Advanced Configuration

### Custom Question Selection
```python
# Example: Custom question selection strategy
preview_request = {
    "topics": ["Excel Formulas", "Data Analysis"],
    "count": 20,
    "difficulty_level": "adaptive",  # Adjusts based on performance
    "exclude_questions": ["q123", "q456"]  # Skip specific questions
}

# Preview questions before starting
response = requests.post(
    "http://localhost:8001/api/v1/interview/questions/select",
    json=preview_request
)
```

### Interview Customization
```json
{
    "candidate_name": "Senior Developer Interview",
    "topics": ["Advanced Excel", "VBA", "Data Modeling"],
    "total_questions": 25,
    "difficulty_level": "hard",
    "custom_settings": {
        "time_limit_per_question": 300,
        "allow_clarifications": true,
        "adaptive_difficulty": true
    }
}
```

## 📊 Data Analysis Examples

### Performance Trends
```python
# Analyze performance trends over time
import pandas as pd
import plotly.express as px

# Get historical data
sessions = get_completed_sessions()
df = pd.DataFrame(sessions)
df['date'] = pd.to_datetime(df['completed_at'])

# Create trend analysis
daily_scores = df.groupby(df['date'].dt.date)['overall_score'].mean()
trend_chart = px.line(
    x=daily_scores.index, 
    y=daily_scores.values,
    title="Average Interview Scores Over Time"
)
```

### Topic Analysis
```python
# Analyze performance by topic
topic_data = []
for session in sessions:
    for topic in session['topics']:
        topic_data.append({
            'topic': topic,
            'score': session['overall_score'],
            'candidate': session['candidate_name']
        })

topic_df = pd.DataFrame(topic_data)
topic_performance = topic_df.groupby('topic')['score'].agg(['mean', 'count', 'std'])
```

## 🚨 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Service Connection Error
```
Error: Cannot connect to the interview service
```
**Solution:**
```bash
# Check if service is running
curl http://localhost:8001/health

# Start the service if not running
cd interview/
python main.py
```

#### 2. No Questions Available
```
Warning: No topics available
```
**Solution:**
```bash
# Generate questions first
cd generator/
python main.py

# Create sample questions
python streamlit_app.py  # Use generator UI
```

#### 3. Session Not Found
```
Error: Interview session not found
```
**Solutions:**
- Check session ID in "⚙️ Session Management"
- Verify session hasn't expired
- Restart from "🚀 Start Interview" if needed

#### 4. Streamlit Import Error
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution:**
```bash
pip install -r interview/streamlit_requirements.txt
```

### Performance Issues

#### Slow Loading
1. **Check API response times**
2. **Reduce question count for testing**
3. **Use local MongoDB instance**
4. **Clear browser cache**

#### Memory Usage
1. **Limit concurrent sessions**
2. **Use pagination for large datasets**
3. **Clear session state periodically**

## 🔗 Integration Examples

### HR System Integration
```python
# Example: Integrate with HR system
class HRSystemIntegration:
    def __init__(self, hr_api_key):
        self.api_key = hr_api_key
    
    def sync_candidates(self):
        """Sync candidates from HR system"""
        candidates = self.get_candidates_from_hr()
        for candidate in candidates:
            self.create_interview_session(candidate)
    
    def send_results_to_hr(self, session_id):
        """Send interview results back to HR system"""
        results = get_interview_results(session_id)
        self.post_to_hr_system(results)
```

### Email Notifications
```python
# Example: Email integration
import smtplib
from email.mime.text import MIMEText

def send_interview_completion_email(session_id, candidate_email):
    """Send email when interview is completed"""
    results = get_interview_results(session_id)
    
    message = f"""
    Interview Completed!
    
    Candidate: {results['candidate_name']}
    Score: {results['overall_score']}%
    Performance: {results['performance_level']}
    
    Detailed results available at: http://localhost:8502
    Session ID: {session_id}
    """
    
    send_email(candidate_email, "Interview Results", message)
```

### Webhook Integration
```python
# Example: Webhook notifications
def setup_webhooks():
    """Setup webhook notifications for interview events"""
    webhook_events = {
        "interview_started": "https://api.company.com/webhooks/interview/started",
        "interview_completed": "https://api.company.com/webhooks/interview/completed",
        "evaluation_ready": "https://api.company.com/webhooks/evaluation/ready"
    }
    
    # Register webhooks with the interview service
    for event, url in webhook_events.items():
        register_webhook(event, url)
```

## 📝 Best Practices

### Interview Conduct
1. **Prepare Environment**: Ensure quiet, distraction-free space
2. **Test Technology**: Verify all systems work before interview
3. **Set Expectations**: Explain the process to candidates
4. **Monitor Progress**: Keep an eye on session progress
5. **Provide Support**: Be available for technical issues

### Data Management
1. **Regular Backups**: Backup interview data regularly
2. **Data Privacy**: Follow data protection regulations
3. **Session Cleanup**: Archive old sessions periodically
4. **Performance Monitoring**: Monitor system performance

### Scalability
1. **Load Testing**: Test with multiple concurrent interviews
2. **Resource Planning**: Monitor CPU, memory, and database usage
3. **Caching Strategy**: Implement caching for frequently accessed data
4. **Service Monitoring**: Set up health checks and alerts

## 🎓 Training Materials

### For Interviewers
1. **System Overview**: Understanding the AI interview process
2. **Question Types**: Working with MCQ and descriptive questions
3. **Evaluation Criteria**: Understanding AI evaluation metrics
4. **Common Scenarios**: Handling different interview situations

### For Candidates
1. **Interface Guide**: How to navigate the interview interface
2. **Technical Requirements**: System requirements and setup
3. **Question Format**: Understanding different question types
4. **Support Options**: Getting help during the interview

### For Administrators
1. **System Administration**: Managing the interview service
2. **User Management**: Adding and managing interviewers
3. **Data Analysis**: Interpreting analytics and reports
4. **Troubleshooting**: Common issues and solutions

---

For more examples and advanced usage, refer to the API documentation at http://localhost:8001/docs 