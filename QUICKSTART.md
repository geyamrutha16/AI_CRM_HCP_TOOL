# ⚡ AI-CRM HCP - Quick Start Guide

Get the AI-CRM Healthcare Interaction Logger running in 5 minutes!

---

## Prerequisites

- **Node.js 16+** & **npm** - [Download](https://nodejs.org)
- **Python 3.9+** - [Download](https://python.org)
- **MySQL 5.7+** - [Download](https://dev.mysql.com/downloads/mysql/) or use existing server
- **Groq API Key** - [Get free key](https://groq.com)

---

## 🚀 Setup in 5 Minutes

### Option 1: Quick Setup (Recommended for first-time)

#### Step 1: Clone/Extract Project

```bash
cd ai-crm-hcp
```

#### Step 2: Set Up MySQL (using Docker)

```bash
# If you have Docker installed
docker run -d \
  --name mysql_crm \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=ai_crm_hcp \
  -p 3306:3306 \
  mysql:8.0

# Create the database user
docker exec -it mysql_crm mysql -uroot -proot -e \
  "CREATE USER 'crm_user'@'%' IDENTIFIED BY 'crm_password'; \
   GRANT ALL PRIVILEGES ON ai_crm_hcp.* TO 'crm_user'@'%'; \
   FLUSH PRIVILEGES;"
```

#### Step 3: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your settings
# Update: GROQ_API_KEY=your_key_here
```

**Edit `.env` file:**

```env
DATABASE_URL=mysql+pymysql://crm_user:crm_password@localhost:3306/ai_crm_hcp
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=dev-secret-key
DEBUG=True
```

#### Step 4: Start Backend

```bash
python main.py
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
⚡ Initializing database...
✅ Database initialized
```

#### Step 5: Frontend Setup (in new terminal)

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

You should see:

```
VITE v5.0.0  ready in 500 ms
➜  Local:   http://localhost:5173/
```

#### Step 6: Open Browser

Navigate to: **http://localhost:5173**

✅ **You're ready to use the AI-CRM!**

---

---

## 🧪 Test the System

### 1. Chat Mode Test

1. Click **💬 Chat Mode** tab
2. Type: `"I just met with Dr. Smith. We discussed our new product. He seemed very interested."`
3. Press Enter or click Send
4. Watch the AI extract and create an interaction!

### 2. Form Mode Test

1. Click **📋 Form Mode** tab
2. Fill in:
   - **Doctor Name**: Dr. Johnson
   - **Interaction Details**: Had a great meeting about pricing models
   - **Sentiment**: Positive
   - **Follow-up**: Schedule demo next week
3. Click **Save Interaction**
4. See success notification!

### 3. View Interactions

1. Click **📊 All Interactions** tab
2. You should see your created interactions
3. Try searching or editing

### 4. Check Backend API

Open: **http://localhost:8000/docs**

This opens interactive API documentation where you can test endpoints!

---

## 💡 Example Prompts to Try

### Simple Log

```
"Met with Dr. Brown today. Discussed Product X effectiveness. She requested additional clinical data."
```

### Complex Interaction

```
"Had a 30-minute call with Dr. Patel. Started skeptical about pricing, but after showing ROI analysis, he warmed up significantly. Wants to arrange a pilot program."
```

### Feedback Request

```
"What should be my follow-up strategy for Dr. Wilson after our interaction went negatively today?"
```

### Data Extraction

```
"Please extract and analyze sentiment from this conversation: 'Dr. Garcia was enthusiastic about our approach and wants to discuss implementation next month.'"
```

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error: "Connection refused" (MySQL)**

```bash
# Check if MySQL is running
mysql -uroot -proot -e "SELECT 1;"

# Or verify Docker container
docker ps | grep mysql
```

**Error: "Groq API key invalid"**

- Get free API key: https://groq.com
- Update `.env` file: `GROQ_API_KEY=your_key_here`
- Restart backend

### Frontend Shows Blank Page

```bash
# Clear cache and restart
cd frontend
npm run dev  # Press Ctrl+F5 in browser
```

### API Not Responding

```bash
# Check if backend is running
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","environment":"development"}
```

### "Database already exists" Error

```bash
# Drop and recreate
mysql -u root -p -e "DROP DATABASE ai_crm_hcp; CREATE DATABASE ai_crm_hcp;"

# Then recreate user and restart backend
mysql -u root -p
# In MySQL prompt, run the SQL from Step 2 again
python main.py
```

---

## 📊 What Happens Behind the Scenes

### When You Chat:

1. **Message Sent** → Frontend Redux store
2. **API Call** → `/agent/run` endpoint
3. **LangGraph Agent** → Analyzes intent
4. **LLM (Groq)** → Extracts structured data
5. **Tool Executed** → Data saved to MySQL
6. **Response** → AI message + structured data
7. **UI Updates** → Chat history + interaction created

### When You Use Form:

1. **Form Validation** → Frontend checks required fields
2. **API Call** → `/interaction` POST endpoint
3. **Save to DB** → MySQL stores record
4. **Response** → Created interaction data
5. **UI Updates** → Toast notification + list refresh

---

## 🎯 Next Steps

After getting it working:

1. **Read Architecture**: Check `ARCHITECTURE.md` for technical details
2. **Explore API Docs**: Go to http://localhost:8000/docs
3. **Try Different Interactions**: Log various interaction types
4. **Customize**: Modify prompts in `backend/langgraph/tools.py`
5. **Deploy**: See deployment instructions in main README.md

---

## 📞 Getting Help

### Common Issues & Solutions

| Issue                  | Solution                                |
| ---------------------- | --------------------------------------- |
| Port 8000 in use       | `lsof -i :8000` then `kill -9 <PID>`    |
| Port 5173 in use       | Change in `vite.config.js`              |
| MySQL connection fails | Check DATABASE_URL in .env              |
| API timeout            | Groq API might be slow, wait 30 seconds |
| Backend errors         | Check terminal for full error message   |

### Debug Mode

Enable verbose logging:

```python
# In backend config.py
DEBUG = True  # Already set in .env
```

### Check Logs

```bash
# Backend logs (in terminal where you run python main.py)
# Frontend logs (browser console - F12)
```

---

## 🎉 You're All Set!

```
✅ Backend: http://localhost:8000
✅ Frontend: http://localhost:5173
✅ Database: MySQL running
✅ LLM: Groq ready
✅ Agent: LangGraph active

🚀 Start logging HCP interactions!
```

---

## 💻 IDE Setup (Optional)

### VS Code Extensions Recommended

- Python
- Pylance
- Thunder Client (API testing)
- ES7+ React/Redux/React-Native snippets
- MySQL

### Run in VS Code

Press `F5` to start debugging (if `.vscode/launch.json` configured)

---

## 🚀 Production Deployment

When ready for production:

1. **Build Frontend**:

   ```bash
   cd frontend
   npm run build
   # Creates dist/ folder for deployment
   ```

2. **Deploy Backend**:
   - Use Railway.app, Render, or AWS
   - Set environment variables
   - Use managed MySQL database

3. **Deploy Frontend**:
   - Upload dist/ to Vercel, Netlify, or S3

See main `README.md` for production setup details.

---

**Happy CRM logging! 🎉**

_For questions, check README.md or ARCHITECTURE.md_
