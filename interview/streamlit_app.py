import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# Configure page
st.set_page_config(
    page_title="AI Interview Service",
    page_icon="��",
    layout="wide"
)

# API Configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001/api/v1/interview")

# Custom CSS for simple, clean UI
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .question-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_connection() -> bool:
    """Check if the API service is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    st.markdown('<h1 class="main-header">🤖 AI Interview Service</h1>', unsafe_allow_html=True)
    
    # Check API connection
    if not check_api_connection():
        st.error("⚠️ Cannot connect to the Interview API service. Please make sure it's running on http://localhost:8001")
        st.info("Start the service by running: `python -m interview.main`")
        return
    
    # Navigation
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "🚀 Start Interview", "💬 Take Interview", "📊 View Results", "📋 Sessions"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🚀 Start Interview":
        show_start_interview()
    elif page == "💬 Take Interview":
        show_take_interview()
    elif page == "📊 View Results":
        show_view_results()
    elif page == "📋 Sessions":
        show_sessions()

def show_dashboard():
    """Dashboard with service overview"""
    st.header("📊 Dashboard")
    
    try:
        # Get stats
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Interviews", stats["total_interviews"])
            
            with col2:
                st.metric("Active Interviews", stats["active_interviews"])
            
            with col3:
                st.metric("Completed Interviews", stats["completed_interviews"])
            
            with col4:
                st.metric("Average Score", f"{stats['average_score']:.1f}")
            
            # Show popular topics
            if stats["popular_topics"]:
                st.subheader("Popular Topics")
                topics_df = pd.DataFrame(
                    list(stats["popular_topics"].items()),
                    columns=["Topic", "Count"]
                )
                st.dataframe(topics_df, use_container_width=True)
        else:
            st.error("Failed to load dashboard data")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

def show_start_interview():
    """Start a new interview"""
    st.header("🚀 Start New Interview")
    
    with st.form("start_interview_form"):
        # Candidate details
        st.subheader("Candidate Information")
        candidate_name = st.text_input("Candidate Name *", placeholder="Enter candidate's full name")
        candidate_email = st.text_input("Email (Optional)", placeholder="candidate@example.com")
        
        # Interview configuration
        st.subheader("Interview Configuration")
        
        # Topics selection
        available_topics = [
            "Excel Formulas", "VBA Programming", "Data Analysis", 
            "Pivot Tables", "Charts and Visualization", "Macros",
            "Financial Modeling", "Database Functions"
        ]
        
        selected_topics = st.multiselect(
            "Select Topics *",
            available_topics,
            help="Choose one or more topics for the interview"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            total_questions = st.slider("Number of Questions", 5, 25, 10)
        
        with col2:
            difficulty_level = st.selectbox(
                "Difficulty Level",
                ["mixed", "easy", "medium", "hard"],
                help="Mixed provides a balanced selection"
            )
        
        # Submit button
        submitted = st.form_submit_button("Start Interview", type="primary")
        
        if submitted:
            if not candidate_name:
                st.error("Please enter the candidate's name")
                return
            
            if not selected_topics:
                st.error("Please select at least one topic")
                return
            
            # Start interview
            try:
                payload = {
                    "candidate_name": candidate_name,
                    "candidate_email": candidate_email if candidate_email else None,
                    "topics": selected_topics,
                    "total_questions": total_questions,
                    "difficulty_level": difficulty_level
                }
                
                response = requests.post(f"{API_BASE_URL}/start", json=payload)
                
                if response.status_code == 200:
                    session_data = response.json()
                    st.success(f"✅ Interview started successfully!")
                    
                    # Store session ID for easy access
                    st.session_state.current_session_id = session_data["session_id"]
                    
                    # Show session details
                    st.info(f"**Session ID:** {session_data['session_id']}")
                    st.info(f"**Topics:** {', '.join(selected_topics)}")
                    st.info(f"**Questions:** {total_questions}")
                    
                    st.info("👉 Go to 'Take Interview' to begin the interview.")
                    
                else:
                    st.error(f"Failed to start interview: {response.text}")
            
            except Exception as e:
                st.error(f"Error starting interview: {e}")

def show_take_interview():
    """Take an interview"""
    st.header("💬 Take Interview")
    
    # Session selection
    session_id = st.text_input(
        "Session ID",
        value=st.session_state.get("current_session_id", ""),
        help="Enter the session ID or use the one from starting an interview"
    )
    
    if not session_id:
        st.info("Please enter a session ID to begin the interview.")
        return
    
    try:
        # Get current question
        response = requests.get(f"{API_BASE_URL}/session/{session_id}/question")
        
        if response.status_code == 400 and "completed" in response.text:
            st.success("🎉 Interview completed! Go to 'View Results' to see the evaluation.")
            return
        
        if response.status_code != 200:
            st.error(f"Error getting question: {response.text}")
            return
        
        question_data = response.json()
        
        # Display question
        st.markdown(f"""
        <div class="question-box">
            <h3>Question {question_data['question_number']} of {question_data['total_questions']}</h3>
            <p>{question_data['context']}</p>
            <h4>{question_data['question_text']}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Answer input
        with st.form("answer_form"):
            if question_data['question_type'] == 'mcq' and question_data['options']:
                # Multiple choice question
                st.write("**Select the best answer:**")
                selected_option = st.radio(
                    "Options:",
                    question_data['options'],
                    key=f"mcq_{question_data['question_id']}"
                )
                answer_text = selected_option
            else:
                # Descriptive question
                st.write("**Provide your answer:**")
                answer_text = st.text_area(
                    "Your answer:",
                    height=150,
                    key=f"desc_{question_data['question_id']}",
                    help="Please provide a detailed answer"
                )
                selected_option = None
            
            # Time tracking
            start_time = st.session_state.get(f"start_time_{question_data['question_id']}", datetime.now())
            st.session_state[f"start_time_{question_data['question_id']}"] = start_time
            
            col1, col2 = st.columns([3, 1])
            with col1:
                submitted = st.form_submit_button("Submit Answer", type="primary")
            with col2:
                clarification = st.form_submit_button("Ask for Clarification")
            
            if clarification:
                # Handle clarification request
                clarification_text = st.text_input("What would you like clarified?")
                if clarification_text:
                    clarify_payload = {
                        "session_id": session_id,
                        "message": clarification_text
                    }
                    clarify_response = requests.post(
                        f"{API_BASE_URL}/session/{session_id}/conversation",
                        json=clarify_payload
                    )
                    if clarify_response.status_code == 200:
                        clarify_data = clarify_response.json()
                        st.info(f"**Clarification:** {clarify_data['response']}")
            
            if submitted:
                if not answer_text or (question_data['question_type'] == 'mcq' and not selected_option):
                    st.error("Please provide an answer before submitting")
                    return
                
                # Calculate time spent
                time_spent = int((datetime.now() - start_time).total_seconds())
                
                # Submit answer
                submit_payload = {
                    "session_id": session_id,
                    "answer": answer_text,
                    "selected_option": selected_option,
                    "time_spent_seconds": time_spent
                }
                
                submit_response = requests.post(
                    f"{API_BASE_URL}/session/{session_id}/answer",
                    json=submit_payload
                )
                
                if submit_response.status_code == 200:
                    result = submit_response.json()
                    
                    # Show feedback
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>Response:</strong> {result['message']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if result['is_interview_complete']:
                        st.success("🎉 Interview completed! Your responses are being evaluated.")
                        st.info("👉 Go to 'View Results' to see your evaluation.")
                    else:
                        st.info("Click 'Submit Answer' again to continue to the next question")
                        # Clear the start time for next question
                        if f"start_time_{question_data['question_id']}" in st.session_state:
                            del st.session_state[f"start_time_{question_data['question_id']}"]
                        st.rerun()
                else:
                    st.error(f"Error submitting answer: {submit_response.text}")
    
    except Exception as e:
        st.error(f"Error during interview: {e}")

def show_view_results():
    """View interview results"""
    st.header("📊 View Results")
    
    session_id = st.text_input("Session ID", help="Enter the session ID to view results")
    
    if not session_id:
        st.info("Please enter a session ID to view results.")
        return
    
    try:
        # Get evaluation
        response = requests.get(f"{API_BASE_URL}/session/{session_id}/evaluation")
        
        if response.status_code == 400:
            st.warning("Interview not yet completed or evaluation in progress.")
            return
        
        if response.status_code != 200:
            st.error(f"Error getting evaluation: {response.text}")
            return
        
        evaluation = response.json()
        
        # Display results
        st.subheader(f"Results for {evaluation['candidate_name']}")
        
        # Overall score
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Score", f"{evaluation['overall_score']:.1f}/100")
        with col2:
            st.metric("Performance Level", evaluation['performance_level'].title())
        with col3:
            st.metric("Questions Answered", f"{evaluation['questions_answered']}/{evaluation['total_questions']}")
        
        # Detailed scores
        if evaluation['mcq_score'] or evaluation['descriptive_score']:
            st.subheader("Score Breakdown")
            score_col1, score_col2 = st.columns(2)
            
            if evaluation['mcq_score']:
                with score_col1:
                    st.metric("MCQ Score", f"{evaluation['mcq_score']:.1f}/100")
            
            if evaluation['descriptive_score']:
                with score_col2:
                    st.metric("Descriptive Score", f"{evaluation['descriptive_score']:.1f}/100")
        
        # Performance summary
        if evaluation['performance_summary']:
            st.subheader("Performance Summary")
            st.write(evaluation['performance_summary'])
        
        # Detailed analysis
        if evaluation['detailed_analysis']:
            st.subheader("Detailed Analysis")
            st.write(evaluation['detailed_analysis'])
        
        # Recommendations
        if evaluation['recommendations']:
            st.subheader("Recommendations")
            for i, rec in enumerate(evaluation['recommendations'], 1):
                st.write(f"{i}. {rec}")
    
    except Exception as e:
        st.error(f"Error viewing results: {e}")

def show_sessions():
    """Show all interview sessions"""
    st.header("📋 Interview Sessions")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "active", "completed", "paused", "cancelled"]
        )
    
    with col2:
        limit = st.slider("Number of sessions", 10, 100, 50)
    
    try:
        # Get sessions
        params = {"limit": limit}
        if status_filter != "All":
            params["status"] = status_filter
        
        response = requests.get(f"{API_BASE_URL}/sessions", params=params)
        
        if response.status_code != 200:
            st.error(f"Error getting sessions: {response.text}")
            return
        
        sessions = response.json()
        
        if not sessions:
            st.info("No sessions found.")
            return
        
        # Display sessions table
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                "Session ID": session['session_id'][:8] + "...",
                "Candidate": session['candidate_name'],
                "Status": session['status'].title(),
                "Score": f"{session['overall_score']:.1f}" if session['overall_score'] else "N/A",
                "Progress": f"{session['questions_answered']}/{session['total_questions']}",
                "Started": session['started_at'].split('T')[0] if session['started_at'] else "N/A"
            })
        
        st.dataframe(sessions_data, use_container_width=True)
        
        # Session details
        st.subheader("Session Details")
        selected_session = st.selectbox(
            "Select a session to view details:",
            options=[f"{s['candidate_name']} - {s['session_id'][:8]}..." for s in sessions],
            format_func=lambda x: x
        )
        
        if selected_session:
            # Find the selected session
            session_id = selected_session.split(" - ")[1].replace("...", "")
            full_session = next((s for s in sessions if s['session_id'].startswith(session_id)), None)
            
            if full_session:
                st.json(full_session)
    
    except Exception as e:
        st.error(f"Error loading sessions: {e}")

if __name__ == "__main__":
    main() 