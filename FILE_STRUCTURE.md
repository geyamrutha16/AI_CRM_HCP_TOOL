# 📁 Project File Structure & Reference Guide

Complete breakdown of all files created in the AI-CRM HCP module.

---

## 🎯 Quick File Reference

### Backend Files

#### Configuration & Setup

| File                       | Purpose                         | Key Config                          |
| -------------------------- | ------------------------------- | ----------------------------------- |
| `backend/main.py`          | FastAPI application entry point | Uvicorn server, routes, middleware  |
| `backend/config.py`        | Environment & settings          | DB_URL, GROQ_API_KEY, CORS settings |
| `backend/.env.example`     | Environment variables template  | Copy to `.env` and customize        |
| `backend/requirements.txt` | Python dependencies             | pip install -r file                 |
| `backend/Dockerfile`       | Docker image definition         | For containerized deployment        |

#### Models & Database

| File                         | Purpose                     | Key Classes                                            |
| ---------------------------- | --------------------------- | ------------------------------------------------------ |
| `backend/models/database.py` | SQLAlchemy ORM setup        | `Interaction` model, `SessionLocal`, `get_db()`        |
| `backend/models/schemas.py`  | Pydantic validation schemas | `AgentRequest`, `InteractionResponse`, `AgentResponse` |
| `backend/models/__init__.py` | Package initialization      | Empty (marks as package)                               |

#### LangGraph Agent

| File                            | Purpose                | Key Exports                                   |
| ------------------------------- | ---------------------- | --------------------------------------------- |
| `backend/langgraph/tools.py`    | Tool implementations   | 5 tools: log, summarize, fetch, edit, suggest |
| `backend/langgraph/agent.py`    | Agent orchestration    | `run_agent()`, `agent_graph`                  |
| `backend/langgraph/__init__.py` | Package initialization | Empty (marks as package)                      |

#### API Routes

| File                             | Purpose                | Endpoints                            |
| -------------------------------- | ---------------------- | ------------------------------------ |
| `backend/routes/interactions.py` | CRUD endpoints         | GET, POST, PUT, DELETE /interaction  |
| `backend/routes/agent.py`        | Agent endpoints        | POST /agent/run, POST /agent/analyze |
| `backend/routes/__init__.py`     | Package initialization | Empty (marks as package)             |

---

### Frontend Files

#### Configuration & Setup

| File                      | Purpose           | Key Config                    |
| ------------------------- | ----------------- | ----------------------------- |
| `frontend/package.json`   | NPM dependencies  | React, Redux, Axios, Vite     |
| `frontend/vite.config.js` | Vite build config | Port 5173, API proxy settings |
| `frontend/index.html`     | HTML entry point  | Loads main.jsx, Google Fonts  |
| `frontend/Dockerfile`     | Docker image      | Node alpine, npm build        |

#### Styles

| File                                          | Purpose            | Scope                            |
| --------------------------------------------- | ------------------ | -------------------------------- |
| `frontend/src/index.css`                      | Global base styles | Typography, links, buttons       |
| `frontend/src/App.css`                        | App-level styles   | Toast, animations, scrollbars    |
| `frontend/src/pages/LogInteractionScreen.css` | Page styles        | Header, tabs, layout, responsive |
| `frontend/src/components/ChatInterface.css`   | Chat component     | Messages, input, animations      |
| `frontend/src/components/InteractionForm.css` | Form component     | Form fields, buttons, validation |
| `frontend/src/components/InteractionList.css` | List component     | Table, search, actions           |

#### React Components

| File                                          | Purpose           | Exports                        |
| --------------------------------------------- | ----------------- | ------------------------------ |
| `frontend/src/main.jsx`                       | React entry point | Mounts App to #root            |
| `frontend/src/App.jsx`                        | Root component    | Redux Provider, ToastContainer |
| `frontend/src/pages/LogInteractionScreen.jsx` | Main page         | Chat + Form + List layout      |
| `frontend/src/components/ChatInterface.jsx`   | Chat UI           | Message display, input handler |
| `frontend/src/components/InteractionForm.jsx` | Form UI           | Form fields, validation        |
| `frontend/src/components/InteractionList.jsx` | List UI           | Table, search, edit/delete     |

#### Redux Store

| File                                      | Purpose            | Exports                              |
| ----------------------------------------- | ------------------ | ------------------------------------ |
| `frontend/src/store/store.js`             | Redux store config | `store` instance                     |
| `frontend/src/store/chatSlice.js`         | Chat state         | `addMessage`, `setLoading`, etc.     |
| `frontend/src/store/interactionsSlice.js` | Interactions state | `setInteractions`, `setFilter`, etc. |
| `frontend/src/store/middleware.js`        | Custom middleware  | Utilities for async actions          |

#### Services

| File                           | Purpose    | API Functions                              |
| ------------------------------ | ---------- | ------------------------------------------ |
| `frontend/src/services/api.js` | API client | `agentAPI`, `interactionsAPI`, `systemAPI` |

---

## 📊 Complete File Tree

```
ai-crm-hcp/
├── README.md                          # Main documentation
├── QUICKSTART.md                      # 5-minute setup guide
├── ARCHITECTURE.md                    # Technical architecture
├── .gitignore                         # Git ignore rules
├── docker-compose.yml                 # Multi-container setup
│
├── backend/
│   ├── main.py                        # FastAPI app
│   ├── config.py                      # Configuration
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                   # Environment template
│   ├── Dockerfile                     # Docker image
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py                # SQLAlchemy ORM
│   │   └── schemas.py                 # Pydantic schemas
│   │
│   ├── langgraph/
│   │   ├── __init__.py
│   │   ├── tools.py                   # 5 CRM tools
│   │   └── agent.py                   # Agent orchestration
│   │
│   └── routes/
│       ├── __init__.py
│       ├── interactions.py             # CRUD routes
│       └── agent.py                    # Agent routes
│
└── frontend/
    ├── index.html                     # HTML entry
    ├── vite.config.js                 # Vite config
    ├── package.json                   # Dependencies
    ├── Dockerfile                     # Docker image
    │
    └── src/
        ├── main.jsx                   # React entry
        ├── App.jsx                    # Root component
        ├── App.css                    # App styles
        ├── index.css                  # Global styles
        │
        ├── pages/
        │   ├── LogInteractionScreen.jsx
        │   └── LogInteractionScreen.css
        │
        ├── components/
        │   ├── ChatInterface.jsx
        │   ├── ChatInterface.css
        │   ├── InteractionForm.jsx
        │   ├── InteractionForm.css
        │   ├── InteractionList.jsx
        │   └── InteractionList.css
        │
        ├── store/
        │   ├── store.js
        │   ├── chatSlice.js
        │   ├── interactionsSlice.js
        │   └── middleware.js
        │
        └── services/
            └── api.js
```

---

## 🔑 Key Files Explained

### Backend Entry Point

**File:** `backend/main.py`

- Initializes FastAPI app
- Configures middleware (CORS, error handling)
- Includes routes (interactions, agent)
- Starts database on app startup
- **Run with:** `python main.py`

### LangGraph Agent

**File:** `backend/langgraph/agent.py`

- Core AI orchestration logic
- `AgentState` definition for message flow
- `agent_node()` - reasoning and tool selection
- `tool_node()` - tool execution
- `build_agent_graph()` - workflow construction
- `run_agent()` - main async function

### React Main Component

**File:** `frontend/src/pages/LogInteractionScreen.jsx`

- Combines all UI components
- Manages view switching (Chat/Form/List/Split)
- Health check status display

### Redux Store

**Files:** `frontend/src/store/*.js`

- `chatSlice.js` - manages chat messages
- `interactionsSlice.js` - manages interaction records
- `store.js` - combines slices into Redux store

### API Service

**File:** `frontend/src/services/api.js`

- Axios instance with interceptors
- `agentAPI` - chat/agent endpoints
- `interactionsAPI` - CRUD endpoints
- `systemAPI` - health checks

---

## 🔄 Data Flow Through Key Files

### Chat Flow

```
ChatInterface.jsx (user types)
  → api.js (axios POST /agent/run)
    → agent.py (LangGraph workflow)
      → tools.py (tool execution)
        → database.py (save to DB)
          → agent.py (format response)
            → api.js (return response)
              → ChatInterface.jsx (display)
                → chatSlice.js (Redux update)
```

### Form Flow

```
InteractionForm.jsx (user submits)
  → api.js (axios POST /interaction)
    → interactions.py (route handler)
      → database.py (save to DB)
        → api.js (return response)
          → InteractionForm.jsx (confirmation)
            → interactionsSlice.js (Redux update)
```

### List Display

```
InteractionList.jsx (mount)
  → api.js (axios GET /interaction)
    → interactions.py (route handler)
      → database.py (query records)
        → api.js (return array)
          → InteractionList.jsx (render table)
            → interactionsSlice.js (Redux store)
```

---

## 📝 File Dependencies Map

```
main.py (FastAPI App)
├── config.py (settings)
├── database.py (ORM)
├── schemas.py (validation)
├── interactions.py (routes)
│   ├── database.py
│   ├── schemas.py
│   └── CRUD operations
└── agent.py (routes)
    ├── agent.py (LangGraph)
    │   ├── tools.py
    │   └── LLM calls
    ├── database.py
    └── schemas.py

App.jsx (React Root)
├── LogInteractionScreen.jsx
│   ├── ChatInterface.jsx
│   │   ├── chatSlice.js (Redux)
│   │   └── api.js (Axios)
│   ├── InteractionForm.jsx
│   │   ├── interactionsSlice.js
│   │   └── api.js
│   └── InteractionList.jsx
│       ├── interactionsSlice.js
│       └── api.js
├── store.js (Redux)
│   ├── chatSlice.js
│   └── interactionsSlice.js
└── Toast (notifications)
```

---

## 🚀 Initialization Order

1. **Backend Start**
   - `python main.py`
   - Loads `config.py`
   - Initializes `database.py` (creates tables)
   - Starts FastAPI server
   - Ready at `http://localhost:8000`

2. **Frontend Start**
   - `npm run dev`
   - Loads `main.jsx`
   - Mounts `App.jsx`
   - Initializes Redux store
   - Ready at `http://localhost:5173`

3. **User Action**
   - User interacts with component
   - Component dispatches Redux action
   - API call via `api.js`
   - Backend processes via routes
   - Response updates Redux store
   - Component re-renders

---

## 📚 Documentation Files

| File              | Type      | Content                           |
| ----------------- | --------- | --------------------------------- |
| `README.md`       | Markdown  | Project overview, setup, API docs |
| `QUICKSTART.md`   | Markdown  | 5-minute start guide, examples    |
| `ARCHITECTURE.md` | Markdown  | Technical design, data flows      |
| FILE_STRUCTURE.md | This file | File organization reference       |

---

## 🔐 Configuration Files

| File           | Purpose          | Sensitive Data            |
| -------------- | ---------------- | ------------------------- |
| `.env`         | Runtime config   | GROQ_API_KEY, DB_PASSWORD |
| `.env.example` | Template         | Safe copy, no secrets     |
| `.gitignore`   | Git ignore rules | Prevents .env commit      |
| `config.py`    | Python config    | Loads from .env           |

---

## ✅ Verification Checklist

After setup, verify these files exist:

### Backend

- [ ] `backend/main.py`
- [ ] `backend/config.py`
- [ ] `backend/models/database.py`
- [ ] `backend/models/schemas.py`
- [ ] `backend/langgraph/agent.py`
- [ ] `backend/langgraph/tools.py`
- [ ] `backend/routes/interactions.py`
- [ ] `backend/routes/agent.py`

### Frontend

- [ ] `frontend/src/main.jsx`
- [ ] `frontend/src/App.jsx`
- [ ] `frontend/src/pages/LogInteractionScreen.jsx`
- [ ] `frontend/src/components/ChatInterface.jsx`
- [ ] `frontend/src/components/InteractionForm.jsx`
- [ ] `frontend/src/components/InteractionList.jsx`
- [ ] `frontend/src/store/store.js`
- [ ] `frontend/src/services/api.js`

### Configuration

- [ ] `.gitignore`
- [ ] `docker-compose.yml`
- [ ] `backend/requirements.txt`
- [ ] `backend/.env.example`
- [ ] `frontend/package.json`
- [ ] `frontend/vite.config.js`

### Documentation

- [ ] `README.md`
- [ ] `QUICKSTART.md`
- [ ] `ARCHITECTURE.md`

---

## 🎯 Common File Edits

**Add new tool:** Edit `backend/langgraph/tools.py`  
**Add new route:** Create file in `backend/routes/`  
**Add new component:** Create file in `frontend/src/components/`  
**Add new page:** Create file in `frontend/src/pages/`  
**Customize LLM:** Edit prompts in `backend/langgraph/tools.py`  
**Change styling:** Edit `.css` files in components/  
**Configure API:** Edit `config.py`

---

**File Structure Reference v1.0**  
_for AI-CRM HCP Module_
