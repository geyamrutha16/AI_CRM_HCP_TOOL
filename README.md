# 🏥 AI-CRM HCP Module - Healthcare Interaction Logger

An AI-first Healthcare CRM system for Pharma Sales Representatives to log and manage interactions with Healthcare Professionals (HCPs). Built with **LangGraph** for intelligent AI orchestration, **Groq LLM**, and a modern React frontend.

## 📋 Project Overview

This system provides **two complementary ways** to log HCP interactions:

1. **🤖 Conversational AI Chat** - Natural language-based interaction logging
2. **📋 Structured Form** - Traditional form-based data entry

The backend uses **LangGraph** agents powered by **Groq's llama-3.3-70b-versatile model** to intelligently extract, analyze, and suggest CRM data from conversations. The previous Gemma 2-9B model was decommissioned and is no longer supported, so this supported model is used instead.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                 │
│                                                             │
│  ┌──────────────────────┬──────────────────────────────┐   │
│  │   Chat Interface     │   Interaction Form           │   │
│  │   (Right Panel)      │   (Left Panel)               │   │
│  │                      │                              │   │
│  │  • Message History   │  • Doctor Name Input         │   │
│  │  • AI Responses      │  • Text Area                 │   │
│  │  • Tool Results      │  • Sentiment Selection       │   │
│  └──────────────────────┴──────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Interaction List (Table View)              │   │
│  │  • All logged interactions                          │   │
│  │  • Search & Filter                                 │   │
│  │  • Edit/Delete Actions                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│            Redux Store (State Management)                  │
│            • chat messages                                │
│            • interactions data                            │
└─────────────────────────────────────────────────────────────┘
                            ↕ (Axios)
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Python)                 │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes                                          │  │
│  │  • POST   /agent/run         (Chat processing)      │  │
│  │  • POST   /interaction       (Create)               │  │
│  │  • PUT    /interaction/{id}  (Update)               │  │
│  │  • GET    /interaction       (Fetch all)            │  │
│  │  • DELETE /interaction/{id}  (Delete)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↕                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         LangGraph Agent Orchestration                │  │
│  │                                                      │  │
│  │  ┌─────────────────────────────────────────────┐   │  │
│  │  │ Agent Node: Intent Recognition              │   │  │
│  │  │ • Analyzes user message                     │   │  │
│  │  │ • Decides which tool to invoke              │   │  │
│  │  └─────────────────────────────────────────────┘   │  │
│  │                      ↓                              │  │
│  │  ┌─────────────────────────────────────────────┐   │  │
│  │  │ Tool Selection & Execution                  │   │  │
│  │  └─────────────────────────────────────────────┘   │  │
│  │          ↙       ↓        ↘        ↙       ↘       │  │
│  │                                                      │  │
│  │  [Log]  [Summarize]  [Fetch]  [Edit]  [Suggest]   │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↕                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Groq LLM (llama-3.3-70b-versatile)               │  │
│  │  • Extract data from conversations                  │  │
│  │  • Sentiment analysis                              │  │
│  │  • Follow-up suggestions                           │  │
│  │  • Content summarization                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↕                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MySQL Database                                     │  │
│  │                                                      │  │
│  │  interactions Table:                               │  │
│  │  • id (Primary Key)                                │  │
│  │  • doctor_name                                     │  │
│  │  • summary                                         │  │
│  │  • sentiment (positive/neutral/negative)          │  │
│  │  • follow_up                                       │  │
│  │  • interaction_text                                │  │
│  │  • created_at                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **Redux Toolkit** - State management
- **Axios** - HTTP client
- **React Toastify** - Notifications
- **Google Inter Font** - Typography

### Backend

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **MySQL** - Database
- **LangGraph** - AI agent orchestration
- **LangChain** - Tool abstraction layer
- **Groq API** (llama-3.3-70b-versatile) - Due to availability constraints

This ensures compliance + performance.

- **Pydantic** - Data validation

---

## 📂 Project Structure

```
ai-crm-hcp/
│
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example            # Environment variables template
│   │
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models & session
│   │   └── schemas.py          # Pydantic schemas
│   │
│   ├── agents/
│   │   ├── tools.py            # Tool implementations
│   │   ├── agent.py            # Agent orchestration
│   │   └── __init__.py
│   │
│   └── routes/
│       ├── interactions.py      # CRUD endpoints
│       ├── agent.py            # Agent/chat endpoints
│       └── __init__.py
│
├── frontend/
│   ├── index.html              # HTML entry point
│   ├── package.json            # Frontend dependencies
│   ├── vite.config.js          # Vite configuration
│   │
│   └── src/
│       ├── main.jsx            # React entry point
│       ├── App.jsx             # Main component
│       ├── App.css             # Global styles
│       ├── index.css           # Base styles
│       │
│       ├── pages/
│       │   ├── LogInteractionScreen.jsx  # Main page
│       │   └── LogInteractionScreen.css
│       │
│       ├── components/
│       │   ├── ChatInterface.jsx    # Chat component
│       │   ├── ChatInterface.css
│       │   ├── InteractionForm.jsx  # Form component
│       │   ├── InteractionForm.css
│       │   ├── InteractionList.jsx  # List component
│       │   └── InteractionList.css
│       │
│       ├── store/
│       │   ├── store.js         # Redux store config
│       │   ├── chatSlice.js     # Chat state slice
│       │   ├── interactionsSlice.js  # Interactions state
│       │   └── middleware.js    # Custom middleware
│       │
│       └── services/
│           └── api.js           # API client
│
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 16+ & npm/yarn
- **Python** 3.9+
- **MySQL** 8.0+ (via MySQL Workbench)
- **Groq API Key** (free from https://groq.com)

### Backend Setup

1. **Navigate to backend directory**

   ```bash
   cd backend
   ```

2. **Create Python virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the backend directory:

   ```env
   DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ai_crm_hcp
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your-secure-secret-key
   DEBUG=True
   ```

5. **Create MySQL database using MySQL Workbench**
   - Open MySQL Workbench
   - Connect to your local MySQL server
   - Create a new schema named `ai_crm_hcp`
   - The application will automatically create the tables on first run

6. **Start backend server**

   ```bash
   python main.py
   ```

   Server will run at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Start development server**

   ```bash
   npm run dev
   ```

   Frontend will run at `http://localhost:5173`

---

## 🧠 LangGraph Agent Design

The LangGraph agent serves as an intelligent orchestrator for managing Healthcare Professional (HCP) interactions in a CRM system. Its primary role is to:

- **Process Natural Language Input**: Analyze user messages from sales representatives describing HCP interactions
- **Extract Structured Data**: Use AI to automatically extract key CRM information like doctor names, summaries, sentiment, and follow-up actions
- **Route to Appropriate Tools**: Based on user intent, select and execute the most relevant tool from its available toolkit
- **Maintain Conversation Context**: Keep track of chat history and provide conversational responses
- **Ensure Data Quality**: Validate extracted information and handle edge cases gracefully

The agent uses a state-machine approach with conditional routing:

```python
# Agent State
{
    "messages": [...],           # Conversation history
    "db_session": <Session>,     # Database connection
    "selected_tool": "tool_name",
    "tool_result": {...}
}

# Workflow:
Agent Node → Tool Selection → Tool Node → Results → Agent Node (loop)
```

### Tools Available

The LangGraph agent utilizes five specialized tools for sales-related activities:

1. **log_interaction_tool**
   - **Purpose**: Captures and logs new HCP interactions from natural language descriptions
   - **Functionality**: Uses LLM (llama-3.3-70b-versatile) to extract structured data from raw conversation text. This change was made because `gemma2-9b-it` has been decommissioned and is no longer supported by Groq.
   - **Data Capture Process**:
     - Analyzes user input for doctor names, discussion topics, outcomes
     - Generates concise summaries (2-3 sentences)
     - Performs sentiment analysis (positive/neutral/negative)
     - Suggests follow-up actions based on interaction content
     - Automatically saves to MySQL database with proper validation
   - **Output**: Structured interaction record with all extracted fields

2. **edit_interaction_tool**
   - **Purpose**: Allows modification of existing logged interaction data
   - **Functionality**: Updates specific fields of previously logged interactions
   - **Modification Process**:
     - Accepts interaction ID and field-value pairs to update
     - Validates field names (summary, sentiment, follow_up, doctor_name)
     - Updates database records with new values
     - Provides confirmation of successful updates
   - **Use Cases**: Correcting information, updating follow-up status, refining summaries

3. **fetch_interaction_tool**
   - **Purpose**: Retrieves past interactions for reference and analysis
   - **Functionality**: Queries database with optional filtering
   - **Features**: Filter by doctor name, limit results, sort by recency
   - **Output**: List of interaction records with full details

4. **delete_interaction_tool**

5.**manual_interaction_tool**

---

## 📡 API Endpoints

### Agent Endpoints

#### `POST /agent/run`

Process a user message through the LangGraph agent.

**Request:**

```json
{
  "message": "I met with Dr. Smith to discuss our product X. He was very interested."
}
```

**Response:**

```json
{
  "ai_message": "Great! I've logged your interaction with Dr. Smith. The sentiment appears positive and I suggest a follow-up in 2 weeks.",
  "structured_data": {
    "status": "extracted",
    "data": {
      "doctor_name": "Dr. Smith",
      "summary": "Discussed product X, positive interest shown",
      "sentiment": "positive",
      "follow_up": "Follow-up in 2 weeks"
    }
  },
  "tool_used": "log_interaction_tool",
  "interaction_id": 42
}
```

#### `POST /agent/analyze`

Analyze sentiment of interaction text.

**Request:**

```json
{
  "text": "The doctor seemed skeptical about the pricing."
}
```

**Response:**

```json
{
  "sentiment": "negative",
  "confidence": 0.87,
  "emotions": ["skeptical", "concerned"]
}
```

### Interaction Endpoints

#### `GET /interaction`

Retrieve all interactions with pagination and filtering.

**Query Parameters:**

- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Max records to return (default: 10)
- `doctor_name` (string): Filter by doctor name

**Response:**

```json
[
  {
    "id": 1,
    "doctor_name": "Dr. Smith",
    "summary": "Discussed product efficacy",
    "sentiment": "positive",
    "follow_up": "Follow-up in 2 weeks",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

#### `POST /interaction`

Create a new interaction record.

**Request:**

```json
{
  "doctor_name": "Dr. Johnson",
  "summary": "Reviewed clinical data",
  "sentiment": "neutral",
  "follow_up": "Send additional materials",
  "interaction_text": "Full conversation text here..."
}
```

#### `PUT /interaction/{id}`

Update an existing interaction.

#### `DELETE /interaction/{id}`

Delete an interaction.

#### `GET /health`

System health check.

---

## 💬 Example Prompts to Try

### Chat Mode Examples

1. **Simple Interaction Logging**

   ```
   "I met with Dr. Garcia today. We discussed the efficacy of Product A.
   She seemed interested and asked for clinical trial data."
   ```

2. **Complex Conversation**

   ```
   "Had a meeting with Dr. Patel. Initial skepticism about pricing,
   but after showing ROI data, he warmed up. He wants to try a pilot program."
   ```

---

## 🎯 Key Features

✅ **AI-Powered Data Extraction** - Automatic extraction of structured CRM data using LLM  
✅ **Dual Input Modes** - Chat for natural language, Form for structured input  
✅ **Real-time Sentiment Analysis** - Understand interaction tone automatically  
✅ **Smart Follow-up Suggestions** - AI recommends next steps based on context  
✅ **Full CRUD Operations** - Create, read, update, delete interactions  
✅ **Search & Filter** - Find past interactions quickly  
✅ **Loading States** - User-friendly loading indicators  
✅ **Error Handling** - Graceful error messages with toast notifications  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **Production-Ready** - Clean code, comments, type safety

---

## 🔒 Security Considerations

1. **Environment Variables**: All sensitive keys in `.env` (not committed)
2. **CORS Configuration**: Restricted to localhost in development
3. **Input Validation**: Pydantic schemas validate all inputs
4. **Database**: Parameterized queries prevent SQL injection
5. **Error Handling**: Secrets not exposed in error messages

---

## 📊 Database Schema

### interactions Table

```sql
CREATE TABLE interactions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  doctor_name VARCHAR(255) NOT NULL,
  summary TEXT,
  sentiment VARCHAR(50) DEFAULT 'neutral',
  follow_up TEXT,
  interaction_text TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_doctor_name (doctor_name),
  INDEX idx_created_at (created_at)
);
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use**

```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

**Database connection error**

- Verify MySQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database `ai_crm_hcp` exists

**Groq API not responding**

- Verify `GROQ_API_KEY` is valid
- Check internet connection
- Check Groq API status

### Frontend Issues

**CORS errors**

- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in `config.py`

**Blank page**

- Check browser console for errors
- Clear browser cache: `npm run dev` with hard refresh (Ctrl+Shift+R)

---

## 📈 Performance Optimization

- **Frontend**: Lazy loading, code splitting with Vite
- **Backend**: Connection pooling, database indexing
- **LLM**: Token optimization, caching of frequent queries
- **Caching**: Redis-ready (can be added)

---

## 🤝 Contributing

To extend this system:

1. **Add new tools**: Create in `backend/agents/tools.py`
2. **Add routes**: Create in `backend/routes/`
3. **Add components**: Create in `frontend/src/components/`
4. **Update schemas**: Modify `backend/models/schemas.py`

---

## 📝 License

MIT License - Feel free to use for personal or commercial projects

---

## 📧 Support & Questions

For issues or questions:

1. Check the troubleshooting section
2. Review the code comments
3. Check FastAPI docs at `/docs`

---

## 🎉 Screenshots & UI

### Main Screen (Split View)

- **Left**: Structured form for manual data entry
- **Right**: Chat interface for conversational logging
- **Top**: Tabs to switch views
- **Bottom**: Recent interactions list (scrollable)

### Chat Mode

- ChatGPT-like interface
- Real-time message updates
- Tool invocation feedback
- Voice input ready (placeholder)

### Form Mode

- Comprehensive interaction details
- Doctor name, summary, sentiment, follow-up
- Form validation with error messages
- Auto-clear after submission

### List Mode

- Complete interaction history
- Search functionality
- Sentiment indicators
- Quick edit/delete actions

---

**Built with ❤️ using LangGraph + Groq LLM**

---

_Last Updated: April 2026_
