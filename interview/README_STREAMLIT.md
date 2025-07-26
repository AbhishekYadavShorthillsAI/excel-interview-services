# AI Interview Service - Streamlit UI

A comprehensive, interactive Streamlit interface for the AI Interview Service that provides an intuitive way to conduct interviews, manage sessions, and analyze results.

## Features

### 🏠 Dashboard
- **Service Overview**: Real-time service status and statistics
- **Key Metrics**: Total interviews, active sessions, available questions
- **Quick Actions**: Direct access to main features
- **Available Topics**: Visual display of interview topics

### 🚀 Start Interview
- **Candidate Management**: Input candidate details
- **Topic Selection**: Multi-select from available topics
- **Configuration**: Set question count and difficulty level
- **Question Preview**: Preview selected questions before starting
- **Instant Launch**: Start interviews immediately

### 💬 Take Interview
- **Interactive Interface**: Conversational interview experience
- **Question Display**: Clean, formatted question presentation
- **Answer Submission**: Support for both MCQ and descriptive answers
- **Progress Tracking**: Visual progress indicator
- **AI Clarification**: Ask for question clarification
- **Real-time Feedback**: Immediate AI feedback on answers

### 📊 View Results
- **Comprehensive Evaluation**: Detailed performance analysis
- **Visual Metrics**: Charts and graphs for score breakdown
- **Topic Performance**: Performance analysis by topic
- **AI Insights**: AI-generated performance summaries
- **Recommendations**: Personalized improvement suggestions
- **Export Options**: Download and share results

### ⚙️ Session Management
- **Session Overview**: View all interview sessions
- **Status Filtering**: Filter by session status
- **Detailed Information**: Complete session details
- **Action Management**: Continue, view, or delete sessions
- **Bulk Operations**: Manage multiple sessions

### 📈 Analytics Dashboard
- **Performance Metrics**: Overall system analytics
- **Score Distribution**: Visual performance distribution
- **Popular Topics**: Most frequently used topics
- **Trend Analysis**: Time-based interview trends
- **Export Tools**: Data export capabilities

## Installation & Setup

### Prerequisites
- Python 3.8+
- Interview Service running on port 8001
- MongoDB database with questions data

### Installation
1. **Install Dependencies**:
   ```bash
   pip install -r interview/streamlit_requirements.txt
   ```

2. **Configure Environment** (Optional):
   ```bash
   # Create .env file if needed
   echo "API_BASE_URL=http://localhost:8001" > .env
   ```

### Running the Application

#### Development Mode
```bash
# From the project root
streamlit run interview/streamlit_app.py --server.port 8502
```

#### Production Mode
```bash
# With custom configuration
streamlit run interview/streamlit_app.py --server.port 8502 --server.headless true
```

#### Docker Deployment
```dockerfile
# Add to existing Dockerfile
COPY interview/streamlit_requirements.txt /app/
RUN pip install -r streamlit_requirements.txt

# Expose Streamlit port
EXPOSE 8502

# Run Streamlit (can be run alongside FastAPI)
CMD ["streamlit", "run", "interview/streamlit_app.py", "--server.port", "8502", "--server.headless", "true"]
```

## Usage Guide

### Starting Your First Interview

1. **Launch the Application**:
   - Navigate to http://localhost:8502
   - Check service status in the sidebar

2. **Create an Interview**:
   - Go to "🚀 Start Interview"
   - Enter candidate information
   - Select topics from available options
   - Configure question count and difficulty
   - Click "Start Interview"

3. **Conduct the Interview**:
   - Switch to "💬 Take Interview"
   - Select the active session
   - Present questions to candidates
   - Submit answers and get AI feedback
   - Continue until completion

4. **Review Results**:
   - Navigate to "📊 View Results"
   - Enter session ID or select from recent interviews
   - Review comprehensive evaluation and insights

### Managing Multiple Sessions

1. **Session Overview**:
   - Use "⚙️ Session Management" for all sessions
   - Filter by status (active, completed, etc.)
   - View detailed session information

2. **Continuing Interviews**:
   - Click "Continue" for active sessions
   - Resume from the last question
   - Maintain conversation context

### Analytics and Reporting

1. **System Analytics**:
   - Access "📈 Analytics Dashboard"
   - View performance trends and distributions
   - Monitor popular topics and success rates

2. **Export Data**:
   - Download session results as reports
   - Export analytics data for external analysis
   - Email results to stakeholders

## Configuration

### API Configuration
The application connects to the Interview Service API. Configure the base URL:

```python
# In streamlit_app.py
API_BASE_URL = "http://localhost:8001/api/v1/interview"
```

### UI Customization
Customize the interface in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"          # Main accent color
backgroundColor = "#ffffff"        # Background color
secondaryBackgroundColor = "#f0f8ff"  # Secondary background
textColor = "#262730"             # Text color
```

### Performance Settings
Optimize for different environments:

```toml
[server]
headless = true                   # For production
port = 8502                      # Custom port
maxUploadSize = 50               # File upload limit (MB)
enableCORS = false               # CORS settings
```

## Features Deep Dive

### Interview Flow Management
- **Session State**: Maintains interview state across page navigation
- **Progress Persistence**: Remembers current question and progress
- **Context Preservation**: Maintains conversation history
- **Error Recovery**: Handles interruptions gracefully

### AI Integration
- **Real-time Feedback**: Immediate AI responses to answers
- **Clarification Support**: AI-powered question clarification
- **Performance Analysis**: AI-generated insights and recommendations
- **Adaptive Questioning**: Context-aware follow-up questions

### Data Visualization
- **Performance Charts**: Interactive Plotly visualizations
- **Score Distributions**: Pie charts and bar graphs
- **Trend Analysis**: Time-series performance tracking
- **Topic Breakdown**: Category-wise performance analysis

## Troubleshooting

### Common Issues

1. **Service Connection Error**:
   ```
   Cannot connect to the interview service
   ```
   - **Solution**: Ensure Interview Service is running on port 8001
   - **Check**: `curl http://localhost:8001/health`

2. **No Questions Available**:
   ```
   No topics available. Please ensure questions are generated first.
   ```
   - **Solution**: Run the Generator Service to create questions
   - **Check**: Verify MongoDB has question data

3. **Session Not Found**:
   ```
   Interview session not found
   ```
   - **Solution**: Verify session ID is correct
   - **Check**: Use Session Management to view active sessions

### Performance Optimization

1. **Memory Usage**:
   - Set reasonable pagination limits
   - Clear session state when not needed
   - Use caching for repeated API calls

2. **API Response Times**:
   - Implement loading indicators
   - Use background tasks for heavy operations
   - Cache static data (topics, question counts)

3. **UI Responsiveness**:
   - Use columns for better layout
   - Implement progressive loading
   - Minimize full page reloads

## Security Considerations

### Data Protection
- **Session Management**: Secure session ID handling
- **Input Validation**: Sanitize all user inputs
- **API Security**: Validate all API responses

### Access Control
- **Authentication**: Can be integrated with existing auth systems
- **Authorization**: Role-based access for different user types
- **Audit Logging**: Track user actions and API calls

## Integration Examples

### External Authentication
```python
# Add to streamlit_app.py for authentication
def check_authentication():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Show login form
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Validate credentials
            if validate_user(username, password):
                st.session_state.authenticated = True
                st.rerun()
```

### Email Integration
```python
# Add email functionality
def send_results_email(session_id, recipient):
    results = make_api_request(f"/session/{session_id}/evaluation")
    
    # Format email with results
    email_content = format_results_email(results)
    
    # Send email (implementation depends on email service)
    send_email(recipient, "Interview Results", email_content)
```

### Webhook Integration
```python
# Add webhook notifications
def notify_completion(session_id):
    webhook_url = os.getenv("COMPLETION_WEBHOOK_URL")
    if webhook_url:
        payload = {
            "event": "interview_completed",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        requests.post(webhook_url, json=payload)
```

## Future Enhancements

### Planned Features
- **Real-time Collaboration**: Multiple interviewers
- **Video Integration**: Video call capabilities
- **Mobile Optimization**: Enhanced mobile experience
- **Advanced Analytics**: Machine learning insights
- **Multi-language Support**: Internationalization

### Extension Points
- **Custom Question Types**: Plugin architecture for new question formats
- **Third-party Integrations**: HR systems, ATS integration
- **Advanced Reporting**: Customizable report templates
- **API Extensions**: Custom endpoints for specific needs

## Support

### Documentation
- **API Documentation**: Available at http://localhost:8001/docs
- **Service README**: See `interview/README.md`
- **Generator Service**: See `generator/README_STREAMLIT.md`

### Community
- **Issues**: Report issues in the project repository
- **Discussions**: Join community discussions
- **Contributions**: Contribute to the project

### Professional Support
- **Enterprise Support**: Available for enterprise deployments
- **Custom Development**: Customization and integration services
- **Training**: User training and onboarding support

---

For technical support or feature requests, please refer to the project documentation or contact the development team. 