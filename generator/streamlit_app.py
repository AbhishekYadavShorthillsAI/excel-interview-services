import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional

# Configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Page configuration
st.set_page_config(
    page_title="Excel Interview Question Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #28a745;
        color: white;
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-right: 2rem;
    }
    
    .tool-call {
        background-color: #fd7e14;
        color: white;
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #dc3545;
    }
    
    .tool-result {
        background-color: #6c757d;
        color: white;
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
    
    .question-card {
        background-color: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .mcq-tag {
        background-color: #17a2b8;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    
    .descriptive-tag {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "stats" not in st.session_state:
        st.session_state.stats = {}
    
def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
    """Make API request to the generator service"""
    try:
        url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def render_chat_message(message: Dict, index: int):
    """Render a single chat message with appropriate styling
    
    Handles all message types returned from /chat endpoint:
    - User messages: role="user" 
    - Assistant messages: role="assistant" (may include tool_calls)
    - Tool results: role="tool" with tool_name
    """
    role = message.get("role", "")
    content = message.get("content", "")
    tool_calls = message.get("tool_calls", [])
    tool_name = message.get("tool_name", "")
    
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 You:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    
    elif role == "assistant":
        # Assistant message - always show the content first
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🤖 Assistant:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # If this assistant message includes tool calls, display them
        if tool_calls:
            for i, tool_call in enumerate(tool_calls):
                call_name = tool_call.get("name", "Unknown Tool")
                call_args = tool_call.get("args", {})
                
                st.markdown(f"""
                <div class="tool-call">
                    <strong>🔧 Tool Call: {call_name}</strong><br>
                    <details>
                        <summary>View Arguments</summary>
                        <pre style="background-color: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem; white-space: pre-wrap;">{json.dumps(call_args, indent=2)}</pre>
                    </details>
                </div>
                """, unsafe_allow_html=True)
    
    elif role == "tool":
        # Tool execution result
        display_tool_name = tool_name if tool_name else "Unknown Tool"
        st.markdown(f"""
        <div class="tool-result">
            <strong>⚙️ Tool Result ({display_tool_name}):</strong><br>
            <div style="white-space: pre-wrap;">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Fallback for any other message types
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 10px; margin: 0.5rem 0;">
            <strong>🔹 {role.title()}:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

def chat_interface():
    """Main chat interface for the generator"""
    st.markdown('<div class="main-header">🤖 AI Question Generator Chat</div>', unsafe_allow_html=True)
    
    # Chat history display
    st.subheader("💬 Conversation History")
    
    # Show message count if there's history
    if st.session_state.chat_history:
        st.caption(f"📝 {len(st.session_state.chat_history)} messages in conversation")
    
    chat_container = st.container()
    with chat_container:

        print(st.session_state.chat_history)
        if st.session_state.chat_history:
            for i, message in enumerate(st.session_state.chat_history):
                render_chat_message(message, i)
        else:
            st.info("👋 Welcome! Start a conversation to generate Excel interview questions. You can ask for specific topics, question types (MCQ/Descriptive), and quantities.")
            st.markdown("""
            **🎯 How it works:**
            1. Type your question generation request
            2. The AI will analyze your request and make tool calls
            3. You'll see the tool calls and their results in real-time
            4. Questions will be generated and saved to the database
            """)
    
    # Chat input
    st.subheader("✍️ Send Message")
    
    # Example prompts that will trigger tool calls
    st.markdown("**💡 Example prompts (these will show tool calls):**")
    example_prompts = [
        "Generate 5 MCQ questions about Excel formulas and 3 descriptive questions about VBA",
        "I need 8 questions on Pivot Tables - make 5 MCQ and 3 descriptive",
        "Create 4 MCQ questions on Excel charts and 2 descriptive on conditional formatting",
        "Generate 6 questions about Excel data analysis using web research - 4 MCQ and 2 descriptive",
        "Make 10 questions total: 3 MCQ on VLOOKUP, 2 descriptive on macros, and 5 MCQ on pivot tables"
    ]
    
    selected_example = st.selectbox("Choose an example or type your own:", [""] + example_prompts)
    
    # Chat input form
    with st.form("chat_form"):
        user_input = st.text_area(
            "Your message:",
            value=selected_example if selected_example else "",
            height=100,
            placeholder="Ask me to generate Excel interview questions..."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            send_button = st.form_submit_button("Send 📤", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("Clear History 🗑️", use_container_width=True)
    
    # Handle form submissions
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
    
    if send_button and user_input.strip():
        with st.spinner("🤖 AI is thinking..."):
            # Send current chat history and new query to /chat endpoint
            # The endpoint will return the complete updated history including:
            # - Previous conversation
            # - New user message  
            # - Assistant response
            # - Tool calls (if any)
            # - Tool results (if any)
            response = make_api_request("chat", "POST", {
                "history": st.session_state.chat_history,  # Current history
                "query": user_input.strip()  # New user query
            })
            
            if response and "history" in response:
                # Replace entire chat history with the updated history from API
                st.session_state.chat_history = response["history"]
                st.rerun()
            else:
                st.error("❌ Failed to get response from chat endpoint")

def question_management():
    """Question management interface"""
    st.markdown('<div class="main-header">📋 Question Management</div>', unsafe_allow_html=True)
    
    # Refresh questions
    if st.button("🔄 Refresh Questions"):
        with st.spinner("Loading questions..."):
            questions_data = make_api_request("questions")
            if questions_data:
                st.session_state.questions = questions_data
    
    # Load questions if not already loaded
    if not st.session_state.questions:
        with st.spinner("Loading questions..."):
            questions_data = make_api_request("questions")
            if questions_data:
                st.session_state.questions = questions_data
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get available tags
        tags_data = make_api_request("questions/tags")
        available_tags = tags_data.get("tags", []) if tags_data else []
        selected_tag = st.selectbox("Filter by Topic:", ["All"] + available_tags)
    
    with col2:
        question_type_filter = st.selectbox("Filter by Type:", ["All", "MCQ", "Descriptive"])
    
    with col3:
        search_term = st.text_input("🔍 Search in questions:")
    
    # Filter questions
    filtered_questions = st.session_state.questions
    
    if selected_tag != "All":
        filtered_questions = [q for q in filtered_questions if q.get("tag") == selected_tag]
    
    if question_type_filter != "All":
        filter_type = question_type_filter.lower()
        filtered_questions = [q for q in filtered_questions if q.get("question_type") == filter_type]
    
    if search_term:
        filtered_questions = [
            q for q in filtered_questions 
            if search_term.lower() in q.get("question", "").lower() or 
               search_term.lower() in q.get("answer", "").lower()
        ]
    
    st.write(f"📊 Showing {len(filtered_questions)} of {len(st.session_state.questions)} questions")
    
    # Display questions
    for i, question in enumerate(filtered_questions):
        with st.expander(f"Question {i+1}: {question.get('question', '')[:100]}..."):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="question-card">
                    <h4>❓ Question:</h4>
                    <p>{question.get('question', '')}</p>
                    
                    <h4>✅ Answer:</h4>
                    <p>{question.get('answer', '')}</p>
                    
                    {f"<h4>📝 Options:</h4><ul>{''.join([f'<li>{option}</li>' for option in question.get('options', [])])}</ul>" if question.get('options') else ""}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Question metadata
                q_type = question.get('question_type', '').upper()
                tag_class = "mcq-tag" if q_type == "MCQ" else "descriptive-tag"
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div class="{tag_class}">{q_type}</div>
                    <br>
                    <strong>📂 Topic:</strong><br>
                    {question.get('tag', 'Unknown')}
                    <br><br>
                    <strong>📅 Created:</strong><br>
                    {question.get('created_at', '')[:10] if question.get('created_at') else 'Unknown'}
                </div>
                """, unsafe_allow_html=True)
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"delete_{question.get('id')}"):
                    with st.spinner("Deleting question..."):
                        delete_response = make_api_request(f"questions/{question.get('id')}", "DELETE")
                        if delete_response:
                            st.success("Question deleted successfully!")
                            st.rerun()

def direct_generation():
    """Direct question generation interface"""
    st.markdown('<div class="main-header">⚡ Direct Question Generation</div>', unsafe_allow_html=True)
    
    st.info("💡 Use this for quick question generation without conversation flow.")
    
    with st.form("direct_generation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input("📚 Topic:", placeholder="e.g., Excel Formulas, Pivot Tables")
            number = st.number_input("🔢 Number of Questions:", min_value=1, max_value=50, value=5)
        
        with col2:
            question_type = st.selectbox("📝 Question Type:", ["mcq", "descriptive", "mixed"])
        
        generate_button = st.form_submit_button("🚀 Generate Questions", use_container_width=True)
    
    if generate_button and topic:
        with st.spinner("🤖 Generating questions..."):
            response = make_api_request("generate", "POST", {
                "topic": topic,
                "number": number,
                "question_type": question_type
            })
            
            if response:
                if response.get("success"):
                    st.success(f"✅ {response.get('message')}")
                    st.balloons()
                else:
                    st.error(f"❌ {response.get('message')}")

def create_question():
    """Manual question creation interface"""
    st.markdown('<div class="main-header">➕ Create Question Manually</div>', unsafe_allow_html=True)
    
    with st.form("create_question_form"):
        question_text = st.text_area("❓ Question:", height=100)
        answer_text = st.text_area("✅ Answer:", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            q_type = st.selectbox("📝 Question Type:", ["mcq", "descriptive"])
        with col2:
            tag = st.text_input("🏷️ Tag/Topic:")
        
        # Options for MCQ
        options = []
        if q_type == "mcq":
            st.subheader("📝 MCQ Options:")
            for i in range(4):
                option = st.text_input(f"Option {i+1}:", key=f"option_{i}")
                if option:
                    options.append(option)
        
        create_button = st.form_submit_button("✨ Create Question", use_container_width=True)
    
    if create_button and question_text and answer_text and tag:
        question_data = {
            "question": question_text,
            "answer": answer_text,
            "question_type": q_type,
            "tag": tag
        }
        
        if options:
            question_data["options"] = options
        
        with st.spinner("Creating question..."):
            response = make_api_request("questions", "POST", question_data)
            
            if response:
                st.success("✅ Question created successfully!")
                st.balloons()

def statistics_dashboard():
    """Statistics and analytics dashboard"""
    st.markdown('<div class="main-header">📊 Statistics Dashboard</div>', unsafe_allow_html=True)
    
    # Load statistics
    with st.spinner("Loading statistics..."):
        stats_data = make_api_request("stats")
        if stats_data:
            st.session_state.stats = stats_data
    
    if st.session_state.stats:
        stats = st.session_state.stats
        
        # Main statistics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h2>{stats.get('total_questions', 0)}</h2>
                <p>Total Questions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h2>{stats.get('mcq_questions', 0)}</h2>
                <p>MCQ Questions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h2>{stats.get('descriptive_questions', 0)}</h2>
                <p>Descriptive Questions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <h2>{len(stats.get('questions_by_tag', {}))}</h2>
                <p>Topics</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        st.subheader("📈 Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Question type distribution
            type_data = {
                'Type': ['MCQ', 'Descriptive'],
                'Count': [stats.get('mcq_questions', 0), stats.get('descriptive_questions', 0)]
            }
            fig_pie = px.pie(
                values=type_data['Count'], 
                names=type_data['Type'], 
                title="Question Type Distribution",
                color_discrete_sequence=['#17a2b8', '#28a745']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Questions by topic
            if stats.get('questions_by_tag'):
                topics = list(stats['questions_by_tag'].keys())
                counts = list(stats['questions_by_tag'].values())
                
                fig_bar = px.bar(
                    x=topics, 
                    y=counts, 
                    title="Questions by Topic",
                    labels={'x': 'Topic', 'y': 'Number of Questions'},
                    color=counts,
                    color_continuous_scale='viridis'
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

def health_check():
    """Display service health information"""
    # Health endpoint is at /health, not under /api/v1
    health_url = API_BASE_URL.replace("/api/v1", "") + "/health"
    try:
        response = requests.get(health_url)
        if response.status_code == 200:
            health_data = response.json()
        else:
            health_data = None
    except Exception as e:
        health_data = None
    
    if health_data:
        status = health_data.get("status", "unknown")
        if status == "healthy":
            st.success(f"✅ Service Status: {status.upper()}")
            st.info(f"📊 Questions Available: {health_data.get('questions_available', 0)}")
        else:
            st.error(f"❌ Service Status: {status.upper()}")
            st.error(f"Error: {health_data.get('error', 'Unknown error')}")
    else:
        st.error("❌ Cannot connect to the generator service")

def main():
    """Main application"""
    initialize_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎯 Navigation")
        
        # Health check
        st.subheader("🏥 Service Health")
        health_check()
        
        # Navigation menu
        page = st.radio(
            "Choose a page:",
            [
                "🤖 AI Chat",
                "📋 Question Management", 
                "⚡ Direct Generation",
                "➕ Create Question",
                "📊 Statistics"
            ]
        )
        
        st.markdown("---")
        st.markdown("**🔧 API Configuration**")
        new_api_url = st.text_input("API Base URL:", value=API_BASE_URL)
        if new_api_url != API_BASE_URL:
            globals()['API_BASE_URL'] = new_api_url
        
        # Debug mode toggle
        debug_mode = st.checkbox("🐛 Debug Mode", help="Show raw JSON responses for troubleshooting")
        if debug_mode and st.session_state.chat_history:
            with st.expander("🔍 Raw Chat History JSON"):
                st.json(st.session_state.chat_history)
        
        st.markdown("---")
        st.markdown("""
        **📖 About this App**
        
        This is a Streamlit interface for the Excel Interview Question Generator service. 
        
        Key features:
        - 🤖 AI-powered chat with tool calls
        - 📋 Question management
        - ⚡ Direct generation
        - 📊 Analytics dashboard
        """)
    
    # Main content based on selected page
    if page == "🤖 AI Chat":
        chat_interface()
    elif page == "📋 Question Management":
        question_management()
    elif page == "⚡ Direct Generation":
        direct_generation()
    elif page == "➕ Create Question":
        create_question()
    elif page == "📊 Statistics":
        statistics_dashboard()

if __name__ == "__main__":
    main() 