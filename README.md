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

### 2. Configure Database

```bash
# Create PostgreSQL database
createdb pixerse_mcp_db

# Or using psql
psql -U postgres -c "CREATE DATABASE pixerse_mcp_db;"
```

### 3. Environment Variables

Copy `core/config/.env.template` to `core/config/.env` and fill:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/pixerse_mcp_db
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

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

## 🛠️ MCP Tools Available

| Tool | Description |
|------|-------------|
| `projects_list` | List all projects |
| `projects_get` | Get project by ID |
| `members_search` | Search team members |
| `members_get` | Get member details |
| `blogs_list` | List blog posts |
| `blogs_get` | Get blog content |
| `assets_search` | Search assets |
| `assets_get` | Get asset details |

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
