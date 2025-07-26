# 📊 Excel Interview Question Generator - Streamlit UI

A beautiful and comprehensive Streamlit interface for the Excel Interview Question Generator service, featuring AI-powered chat with **tool call visualization** and complete question management capabilities.

## ✨ Features

### 🤖 AI Chat Interface
- **Interactive conversation** with AI for question generation
- **Real-time tool call visualization** - see exactly when and how the AI uses tools
- **Conversation history** with color-coded messages
- **Tool call arguments display** with expandable JSON viewer
- **Tool execution results** showing generation outcomes

### 📋 Question Management
- **Browse all questions** with advanced filtering
- **Search functionality** across questions and answers
- **Filter by topic/tag** and question type (MCQ/Descriptive)
- **Question cards** with full details and metadata
- **Delete functionality** for question cleanup

### ⚡ Direct Generation
- **Quick question generation** without conversation flow
- **Topic-based generation** with customizable parameters
- **Mixed question types** (MCQ, Descriptive, or both)
- **Batch generation** (up to 50 questions at once)

### ➕ Manual Question Creation
- **Form-based question creation** for custom questions
- **MCQ option management** with dynamic fields
- **Topic tagging** for organization
- **Immediate database saving**

### 📊 Analytics Dashboard
- **Real-time statistics** about your question database
- **Visual charts** showing question distribution
- **Topic-wise breakdown** with interactive graphs
- **Performance metrics** and counts

### 🏥 Health Monitoring
- **Service status** monitoring
- **Database connectivity** checks
- **Question count** tracking
- **Error reporting** for troubleshooting

## 🚀 Quick Start

### Prerequisites
1. **Generator Service Running**: Make sure your FastAPI generator service is running on `http://localhost:8000`
2. **Python Environment**: Python 3.8+ recommended

### Option 1: Using the Run Script (Recommended)
```bash
# Navigate to the generator directory
cd generator

# Run the script (it will install dependencies automatically)
python run_streamlit.py
```

### Option 2: Manual Setup
```bash
# Navigate to the generator directory
cd generator

# Install dependencies
pip install -r streamlit_requirements.txt

# Run Streamlit
streamlit run streamlit_app.py
```

### Option 3: Direct Streamlit Command
```bash
# From the generator directory
streamlit run streamlit_app.py --server.port 8501
```

## 🌐 Access the UI

Once running, open your browser and navigate to:
- **Local**: http://localhost:8501
- **Network**: http://your-ip:8501 (if running on a server)

## 🎯 Usage Guide

### 1. AI Chat Interface - Tool Call Visualization

The main highlight of this UI is the **tool call visualization**. Here's what you'll see:

#### Chat Flow with Tool Calls:
1. **User Message** (Blue bubble): Your input request
2. **Assistant Message** (Green bubble): AI's response with tool call summary
3. **Tool Call Display** (Orange box): Shows:
   - Tool name (e.g., `generate_and_save` or `generate_web_research_questions`)
   - Expandable arguments showing topic specifications
   - JSON formatted parameters
4. **Tool Result** (Gray box): Shows the execution result and success message

#### Example Chat Flow:
```
👤 You: "Generate 5 MCQ questions about Excel formulas and 3 descriptive questions about VBA"

🤖 Assistant: "I'll generate questions with the following specifications:
• Excel formulas: 5 MCQ, 0 descriptive  
• VBA: 0 MCQ, 3 descriptive"

🔧 Tool Call: generate_and_save
   View Arguments ▼
   {
     "topic_specifications": [
       {
         "topic": "Excel formulas",
         "mcq_count": 5,
         "descriptive_count": 0
       },
       {
         "topic": "VBA", 
         "mcq_count": 0,
         "descriptive_count": 3
       }
     ]
   }

⚙️ Tool Result (generate_and_save): "Successfully generated and saved 8 questions across 2 topics:
• Excel formulas (5 MCQ, 0 descriptive)
• VBA (0 MCQ, 3 descriptive)"
```

### 2. Example Prompts for Tool Calls

Try these prompts to see different tool calls in action:

#### Basic Generation:
- "Generate 10 MCQ questions about Pivot Tables"
- "I need 5 descriptive questions on Excel macros"

#### Multi-Topic Generation:
- "Create 3 MCQ for Excel formulas and 2 descriptive for data validation"
- "Generate mixed questions: 5 on charts, 3 on conditional formatting"

#### Web Research Generation:
- "Generate questions about latest Excel features using web research"
- "Create current trend questions for Excel data analysis"

### 3. Question Management

- **Filter by Topic**: Use the dropdown to see questions from specific topics
- **Filter by Type**: Show only MCQ or Descriptive questions
- **Search**: Find questions containing specific terms
- **View Details**: Click expanders to see full question details
- **Delete**: Remove unwanted questions (with confirmation)

### 4. Direct Generation

- Use this for quick generation without the chat interface
- Select topic, number of questions, and type
- Results are generated and saved immediately

### 5. Statistics Dashboard

- View real-time analytics about your question database
- Interactive charts showing distribution by type and topic
- Monitor generation progress and database growth

## 🎨 UI Features

### Color-Coded Messages
- 🔵 **Blue**: User messages
- 🟢 **Green**: Assistant responses  
- 🟠 **Orange**: Tool calls (with red left border)
- ⚫ **Gray**: Tool results (with green left border)

### Interactive Elements
- **Expandable tool arguments**: Click to view detailed JSON
- **Collapsible question cards**: Organized display of questions
- **Real-time updates**: Live statistics and health monitoring
- **Responsive design**: Works on desktop and mobile

### Visual Indicators
- **MCQ Tags**: Blue badges for multiple choice questions
- **Descriptive Tags**: Green badges for descriptive questions
- **Status Icons**: Health indicators and loading spinners
- **Progress Feedback**: Success/error messages with emojis

## 🔧 Configuration

### API Configuration
You can change the API endpoint in the sidebar:
- Default: `http://localhost:8000/api/v1`
- Update in the sidebar "API Configuration" section

### Customization
The UI supports easy customization through:
- CSS styling in the `streamlit_app.py` file
- Color schemes and themes
- Layout modifications

## 🐛 Troubleshooting

### Common Issues

1. **"Cannot connect to the generator service"**
   - Ensure your FastAPI service is running on port 8000
   - Check if the API URL in sidebar is correct
   - Verify network connectivity

2. **"No questions showing"**
   - Make sure MongoDB is connected
   - Check if any questions exist in the database
   - Try the "Refresh Questions" button

3. **Tool calls not showing**
   - This indicates the AI isn't using tools
   - Try more specific prompts with clear requirements
   - Check if the generator service is properly configured

4. **Streamlit dependencies issues**
   - Run `pip install -r streamlit_requirements.txt`
   - Use Python 3.8+ for best compatibility

### Health Check
Always check the "Service Health" section in the sidebar for:
- ✅ Service status (healthy/unhealthy)
- 📊 Database connectivity
- 🔢 Available questions count

## 🚀 Advanced Features

### Batch Operations
- Generate up to 50 questions at once
- Multi-topic specifications in single requests
- Bulk management through the UI

### Analytics
- Real-time dashboard updates
- Visual representation of question distribution
- Topic popularity tracking

### Export Capabilities
- View questions in organized format
- Copy question text and answers
- Analyze question patterns

## 📋 Next Steps

After setting up the Streamlit UI:

1. **Test the chat interface** with example prompts
2. **Explore tool call visualization** to understand AI behavior
3. **Generate some questions** to populate the database
4. **Use the analytics dashboard** to monitor your question bank
5. **Customize the UI** to match your preferences

---

**Enjoy your Excel Interview Question Generator with beautiful tool call visualization! 🎉** 