# 🏗️ AI-CRM HCP - Technical Architecture

## Overview

This document provides detailed technical documentation for the AI-CRM HCP module architecture, design decisions, and implementation details.

---

## 1. System Components

### 1.1 Frontend Architecture

**Technology Stack:**

- React 18 with Vite
- Redux Toolkit for state management
- Axios for HTTP communication
- React Toastify for notifications

**Component Hierarchy:**

```
App
├── Provider (Redux)
├── LogInteractionScreen (Main Page)
│   ├── ChatInterface
│   │   ├── Message List
│   │   ├── Input Area
│   │   └── Voice Button
│   ├── InteractionForm
│   │   ├── Doctor Name Input
│   │   ├── Text Area
│   │   ├── Sentiment Selector
│   │   └── Follow-up Input
│   └── InteractionList
│       ├── Search Bar
│       ├── Table
│       └── Pagination
└── ToastContainer
```

**State Management (Redux):**

```javascript
store
├── chat (chatSlice)
│   ├── messages: []
│   ├── loading: false
│   └── error: null
└── interactions (interactionsSlice)
    ├── interactions: []
    ├── currentInteraction: null
    ├── loading: false
    ├── error: null
    └── filter: {...}
```

### 1.2 Backend Architecture

**Technology Stack:**

- FastAPI for REST API
- SQLAlchemy ORM for database
- LangGraph for agent orchestration
- LangChain for tool abstraction
- Groq API for LLM

**Application Structure:**

```
FastAPI App
├── Middleware
│   ├── CORS
│   └── Error Handling
├── Routes
│   ├── /agent/* (Agent operations)
│   └── /interaction/* (CRUD operations)
├── LangGraph Agent
│   ├── Agent Node (reasoning)
│   ├── Tool Node (execution)
│   └── Conditional Edges (routing)
└── Database Layer
    ├── SQLAlchemy Models
    └── Database Session
```

---

## 2. LangGraph Agent Design

### 2.1 Agent State Machine

**State Definition:**

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence, add_messages]  # Conversation history
    db_session: Session                          # Database connection
    selected_tool: str                           # Tool to invoke
    tool_result: dict                            # Tool output
```

### 2.2 Agent Workflow

```
START
  ↓
[Agent Node]
  • Receives user input
  • Analyzes intent with LLM
  • Selects appropriate tool
  ↓
[Router Decision]
  ├─ Tool selected? → [Tool Node]
  └─ No tool? → END
  ↓
[Tool Node]
  • Execute selected tool
  • Format results
  • Return to Agent
  ↓
[Loop back to Agent if needed]
  ↓
END (Return response to user)
```

### 2.3 Tool Selection Logic

The agent uses JSON-based decision making:

```python
# Agent prompt response format
{
    "intent": "User wants to log interaction",
    "selected_tool": "log_interaction_tool",
    "parameters": {...},
    "conversational_response": "I'll save that interaction..."
}
```

---

## 3. Data Flow Diagrams

### 3.1 Chat-based Interaction Flow

```
User Input (Chat)
  ↓
[Frontend - ChatInterface]
  ├─ Add user message to Redux
  ├─ Set loading state
  ├─ Call agentAPI.runAgent()
  ↓
[API Call - Axios POST /agent/run]
  ↓
[Backend - FastAPI]
  ├─ Receive AgentRequest
  ├─ Initialize AgentState
  ├─ Run LangGraph workflow
  ↓
[LangGraph Agent]
  ├─ Agent Node analyzes message
  ├─ Selects tool
  ├─ Tool Node executes
  ├─ Returns result
  ↓
[Database Operations]
  ├─ If log_tool: Save to DB
  ├─ If fetch_tool: Query from DB
  └─ If edit_tool: Update in DB
  ↓
[API Response - AgentResponse]
  ├─ ai_message: "Saved interaction..."
  ├─ structured_data: {extracted data}
  ├─ tool_used: "log_interaction_tool"
  └─ interaction_id: 42
  ↓
[Frontend]
  ├─ Receive response
  ├─ Add AI message to Redux
  ├─ Update interactions if needed
  ├─ Show toast notification
  └─ Clear loading state
  ↓
User sees result
```

### 3.2 Form-based Interaction Flow

```
User fills form
  ↓
Submit clicked
  ↓
[Frontend - InteractionForm]
  ├─ Validate form
  ├─ Call interactionsAPI.create()
  ↓
[API Call - Axios POST /interaction]
  ↓
[Backend - FastAPI]
  ├─ Receive InteractionCreate
  ├─ Validate with Pydantic
  ├─ Create record in DB
  ├─ Return created record
  ↓
[Frontend]
  ├─ Receive response
  ├─ Add to Redux interactions
  ├─ Show success toast
  ├─ Clear form
  └─ Refresh list
  ↓
User sees confirmation
```

---

## 4. Database Schema

### 4.1 Interactions Table

```sql
CREATE TABLE interactions (
  id INT PRIMARY KEY AUTO_INCREMENT,

  -- Core fields
  doctor_name VARCHAR(255) NOT NULL,
  summary TEXT,
  sentiment VARCHAR(50) DEFAULT 'neutral',
  follow_up TEXT,

  -- Raw data
  interaction_text TEXT NOT NULL,

  -- Metadata
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  -- Indexes
  INDEX idx_doctor_name (doctor_name),
  INDEX idx_created_at (created_at),
  INDEX idx_sentiment (sentiment)
);
```

### 4.2 Data Access Patterns

**Create Interaction:**

```python
# From form
db_interaction = Interaction(
    doctor_name="Dr. Smith",
    summary="...",
    sentiment="positive",
    follow_up="...",
    interaction_text="..."
)
db.add(db_interaction)
db.commit()

# From chat (auto-extracted)
extracted = llm_extract_fields(raw_text)
db_interaction = Interaction(**extracted)
db.add(db_interaction)
db.commit()
```

**Fetch Interactions:**

```python
# Get all
interactions = db.query(Interaction)\
    .order_by(Interaction.created_at.desc())\
    .limit(10)\
    .all()

# Filter by doctor
interactions = db.query(Interaction)\
    .filter(Interaction.doctor_name.ilike('%Smith%'))\
    .all()

# Get specific
interaction = db.query(Interaction)\
    .filter(Interaction.id == 42)\
    .first()
```

**Update Interaction:**

```python
interaction = db.query(Interaction).get(id)
interaction.sentiment = "positive"
interaction.follow_up = "New follow-up"
db.commit()
```

---

## 5. LLM Integration (Groq)

### 5.1 LLM Configuration

```python
llm = ChatGroq(
    temperature=0.7,           # Balance creativity and consistency
    model_name="llama-3.3-70b-versatile", # Supported Groq model; gemma2-9b-it was decommissioned
    api_key=config.GROQ_API_KEY
)
```

### 5.2 Tool Prompts

**Log Tool Extraction:**

```
Analyze this healthcare interaction and extract:
1. Doctor's name (confirm or correct from: {name})
2. Summary (2-3 sentences of key points)
3. Sentiment (positive/neutral/negative)
4. Follow-up action (if any)

Interaction text:
{raw_text}

Return as JSON with keys: doctor_name, summary, sentiment, follow_up
```

**Sentiment Analysis:**

```
Analyze sentiment and provide confidence:

Text: "{text}"

Return JSON with:
- sentiment (positive/neutral/negative)
- confidence (0-1)
- emotions (list of detected emotions)
```

**Suggestion Generation:**

```
Based on this HCP interaction, suggest next steps:

Doctor: {doctor_name}
Summary: {summary}
Context: {additional_context}

Provide 2-3 actionable next steps for the sales rep.
```

---

## 6. API Contract

### 6.1 Request/Response Examples

**Agent Run Request:**

```json
{
  "message": "I met with Dr. Smith and discussed Product A. He seemed interested."
}
```

**Agent Run Response:**

```json
{
  "ai_message": "Great! I've logged your interaction with Dr. Smith...",
  "structured_data": {
    "status": "extracted",
    "data": {
      "doctor_name": "Dr. Smith",
      "summary": "Discussed Product A, positive interest",
      "sentiment": "positive",
      "follow_up": "Follow up in 1 week"
    }
  },
  "tool_used": "log_interaction_tool",
  "interaction_id": 42
}
```

**Interaction Create Request:**

```json
{
  "doctor_name": "Dr. Johnson",
  "summary": "Product efficacy discussion",
  "sentiment": "neutral",
  "follow_up": "Send clinical data",
  "interaction_text": "Full conversation..."
}
```

**Interaction Create Response:**

```json
{
  "id": 43,
  "doctor_name": "Dr. Johnson",
  "summary": "Product efficacy discussion",
  "sentiment": "neutral",
  "follow_up": "Send clinical data",
  "interaction_text": "Full conversation...",
  "created_at": "2024-01-15T10:30:00"
}
```

---

## 7. Error Handling

### 7.1 Frontend Error Handling

```javascript
try {
  const response = await agentAPI.runAgent(message);
  // Success handling
} catch (error) {
  const errorMessage = error.response?.data?.detail || "Network error";
  dispatch(setError(errorMessage));
  toast.error(errorMessage);
}
```

### 7.2 Backend Error Handling

```python
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# In routes
if not interaction:
    raise HTTPException(
        status_code=404,
        detail="Interaction not found"
    )
```

---

## 8. Performance Considerations

### 8.1 Frontend Optimization

- **Code Splitting**: Vite automatic chunks
- **Lazy Loading**: React.lazy for components
- **Memoization**: useMemo, useCallback for expensive operations
- **Virtual Scrolling**: For large interaction lists

### 8.2 Backend Optimization

- **Database Indexing**: On doctor_name, created_at, sentiment
- **Connection Pooling**: SQLAlchemy pool configuration
- **Query Optimization**: Proper WHERE clauses and limits
- **Caching**: Redis-ready (to be implemented)

### 8.3 LLM Optimization

- **Token Limits**: Control max_tokens in prompts
- **Temperature**: 0.7 for balance
- **Prompt Engineering**: Concise, clear prompts
- **Streaming**: Supported by Groq API

---

## 9. Security Architecture

### 9.1 Input Validation

```python
# Pydantic validation
class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)

# HTML escaping in frontend
DOMPurify.sanitize(userInput)
```

### 9.2 API Security

```python
# CORS configuration
@app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Rate limiting (to be implemented)
```

### 9.3 Database Security

- **Parameterized Queries**: SQLAlchemy handles escaping
- **Connection Encryption**: SSL/TLS in production
- **User Permissions**: MySQL user with limited privileges

---

## 10. Deployment

### 10.1 Development

```bash
# Backend
python main.py  # Runs on port 8000

# Frontend
npm run dev     # Runs on port 5173
```

### 10.2 Docker

```bash
# Single command deployment
docker-compose up -d
```

### 10.3 Production

- **Frontend**: Deploy to Vercel/Netlify
- **Backend**: Deploy to Railway/Render/AWS
- **Database**: Managed MySQL (AWS RDS/Google Cloud SQL)
- **LLM API**: Groq (cloud)

---

## 11. Future Enhancements

- [ ] Voice input/output integration
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Advanced filtering and reporting
- [ ] Email notifications
- [ ] Calendar integration
- [ ] CRM webhook integration
- [ ] Batch processing
- [ ] Custom agent workflows
- [ ] Model fine-tuning

---

**Architecture Document v1.0**  
_Last Updated: April 2024_
