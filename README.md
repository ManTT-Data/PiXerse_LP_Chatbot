# MCP LP PiX - Chatbot Service

A FastAPI-based chatbot service using Model Context Protocol (MCP) for team information queries.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate
git clone <repo-url>
cd "MCP LP PiX"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

This project uses **two databases**:

**PostgreSQL (Aiven)** - For structured data:
- ✅ Production-ready Aiven PostgreSQL
- ✅ Async SQLAlchemy with proper relationships  
- ✅ Auto-created schema with sample data
- ✅ 9 MCP tools for database queries
- 📁 Stores: Projects, Members, Blogs, Assets

**MongoDB Atlas** - For chat history:
- ✅ Cloud-hosted MongoDB for chat sessions
- ✅ Async Motor driver for high performance
- ✅ Auto-connection on startup
- ✅ RESTful API endpoints for chat management
- 💬 Stores: Chat sessions, messages, user interactions

### 3. Environment Variables

Copy `env.example` to `.env` and configure your credentials:

```bash
cp env.example .env
```

Edit `.env` file with your actual values:
```env
# PostgreSQL Database (Aiven)
DATABASE_URL=postgresql+asyncpg://username:password@host:port/database
DB_URL=postgresql+asyncpg://username:password@host:port/database

# MongoDB Database (Atlas) - for chat history
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=PiXerse_ChatBot
MONGODB_COLLECTION_NAME=chat_sessions
MONGODB_TIMEOUT=5000

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Security
SECRET_KEY=your-super-secret-key-here

# Other configurations...
```

**IMPORTANT**: Never commit `.env` files to git!

### 5. Run Application

```bash
# Method 1: Using main.py
python main.py

# Method 2: Using module
python -m core

# Method 3: Direct uvicorn
uvicorn core.web.application:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 API Endpoints

- **Web Interface**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/api/docs`
- **Health Check**: `http://localhost:8000/health`

### Chat API

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about PiXerse team",
    "conversation_id": "test-123"
  }'
```

## 🛠️ MCP Tools Available (9 Tools)

### 📁 Project Tools
| Tool | Description |
|------|-------------|
| `get_project_by_id` | Get detailed project information by ID |
| `get_projects_description` | List all projects with descriptions |
| `get_projects_by_keywords` | Search projects by keyword in description |

### 👥 Member Tools
| Tool | Description |
|------|-------------|
| `get_member_by_id` | Get detailed member information by ID |
| `get_members_description` | List all team members with summaries |
| `get_members_by_skill_keyword` | Search members by skills/expertise |

### 📝 Blog Tools
| Tool | Description |
|------|-------------|
| `get_blog_by_id` | Get detailed blog content by ID |
| `get_blogs_description` | List all blogs with content previews |
| `get_blogs_by_keyword` | Search blogs by keyword in content |

## 💬 Chat History API Endpoints

RESTful API for managing chat sessions and retrieving conversation history:

### Create Chat Session
```bash
POST /api/chat-history/sessions
Content-Type: application/json

{
  "session_id": "unique_session_id",
  "user_id": "user_123",
  "message": "Hello!",
  "response": "Hi there!",
  "action": "chat"
}
```

### Get Session by ID
```bash
GET /api/chat-history/sessions/{session_id}
```

### Update Session Response
```bash
PATCH /api/chat-history/sessions/{session_id}/response
Content-Type: application/json

{
  "response": "Updated response"
}
```

### Get User Sessions
```bash
GET /api/chat-history/users/{user_id}/sessions?limit=50&skip=0&action=chat
```

### Get Chat History (Formatted)
```bash
# Text format
GET /api/chat-history/users/{user_id}/history?format=text&limit=10

# JSON format
GET /api/chat-history/users/{user_id}/history?format=json&limit=10
```

### Delete User Sessions
```bash
DELETE /api/chat-history/users/{user_id}/sessions
```

## 📁 Project Structure

```
core/
├── config/          # Environment configs
├── db/              # Database & repositories
├── schemas/         # Data models
├── services/        # Business logic & MCP tools
├── web/            # FastAPI app & routes
└── settings/       # App settings

scripts/            # Utility scripts
tests/             # Test files
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Test specific module
pytest tests/test_mcp_tools.py -v

# With coverage
pytest --cov=core tests/
```

## 🐳 Docker (Optional)

```bash
# Build and run
docker build -t mcp-chatbot .
docker run -p 8000:8000 --env-file core/config/.env mcp-chatbot
```

## 🔧 Common Issues

1. **Module not found**: Use `python -m core` instead of `python core`
2. **Database connection**: Check PostgreSQL is running and credentials in `.env`
3. **OpenAI errors**: Verify API key is valid and has credits

## 🚀 Development

```bash
# Format code
black core/ tests/

# Lint
flake8 core/ tests/

# Type check
mypy core/
```

## 📝 Dependencies

Key packages:
- FastAPI + Uvicorn (Web framework)
- SQLAlchemy + PostgreSQL (Database)
- OpenAI (AI integration)
- MCP (Model Context Protocol)

---

**Made by PiXerse Team** 🎯
