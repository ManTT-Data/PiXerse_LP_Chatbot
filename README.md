---
title: PiXerse LP Chatbot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# 🤖 PiXerse LP Chatbot

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A production-ready FastAPI chatbot service using Model Context Protocol (MCP) for team information queries, powered by OpenAI and integrated with PostgreSQL and MongoDB.

## ✨ Features

- 🚀 **FastAPI** - Modern, fast web framework
- 🧠 **MCP Integration** - Model Context Protocol for structured AI interactions
- 🗄️ **Dual Database** - PostgreSQL for structured data + MongoDB for chat history
- 🔄 **Async/Await** - High-performance async operations
- 🐳 **Docker Ready** - Production-ready containerization
- 📊 **Auto Documentation** - Interactive API docs with Swagger UI
- 🔒 **Secure** - Environment-based configuration
- 🌐 **CORS Enabled** - Ready for frontend integration

## 🎯 Use Cases

- Team member information queries
- Project documentation chatbot
- Blog content search and retrieval
- Conversational AI with context awareness

---

## 🚀 Quick Deploy to Hugging Face

### Method 1: One-Click Deploy

1. **Fork this repository** to your GitHub account
2. **Create a new Space** on [Hugging Face](https://huggingface.co/new-space)
3. **Select Docker** as the Space SDK
4. **Connect your GitHub repo**
5. **Configure Secrets** in Space Settings:
   ```
   DATABASE_URL=postgresql+asyncpg://...
   MONGODB_URL=mongodb+srv://...
   OPENAI_API_KEY=sk-proj-...
   SECRET_KEY=your-secret-key
   ```
6. **Deploy!** 🎉

### Method 2: Manual Deploy

```bash
# Clone repository
git clone <your-repo-url>
cd PiXerse_LP_Chatbot

# Install Hugging Face CLI
pip install huggingface_hub

# Login to Hugging Face
huggingface-cli login

# Create and push to Space
huggingface-cli repo create your-space-name --type space --space_sdk docker
git remote add hf https://huggingface.co/spaces/<your-username>/<your-space-name>
git push hf main
```

**Important**: Set environment variables as **Secrets** in your Space Settings!

---

## 🏠 Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL database (or Aiven account)
- MongoDB Atlas account
- OpenAI API key

### 1. Setup Environment

```bash
# Clone repository
git clone <repo-url>
cd PiXerse_LP_Chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `env.example` to `.env` and update with your credentials:

```bash
cp env.example .env
```

Edit `.env` file:
```env
# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://username:password@host:port/database

# MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=PiXerse_ChatBot

# OpenAI API
OPENAI_API_KEY=sk-proj-your-key-here

# Security
SECRET_KEY=your-super-secret-key-here
```

**⚠️ NEVER commit `.env` to git!**

### 3. Run Application

```bash
# Method 1: Using main.py (recommended)
python main.py

# Method 2: Using uvicorn directly
uvicorn core.web.application:app --host 0.0.0.0 --port 8000 --reload

# Method 3: Using module
python -m core
```

### 4. Access Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build Docker image
docker build -t pixerse-chatbot .

# Run container
docker run -d \
  --name pixerse-chatbot \
  -p 7860:7860 \
  --env-file .env \
  pixerse-chatbot
```

### Using Docker Compose (Optional)

```bash
# Create docker-compose.yml (see example below)
docker-compose up -d
```

---

## 📊 Database Architecture

### PostgreSQL (Strapi v5 Schema)

Stores structured data with proper relationships:

| Table | Description |
|-------|-------------|
| `up_users` | User authentication |
| `blogs` | Blog posts and articles |
| `projects` | Team projects |
| `members` | Team members |
| `categories`, `tags`, `authors` | Blog metadata |
| `technologies` | Project technologies |
| Link tables | Many-to-many relationships |

### MongoDB Atlas

Stores conversational data:

```json
{
  "session_id": "unique_id",
  "user_id": "user_123",
  "message": "User message",
  "response": "Bot response",
  "timestamp": "2025-10-01T10:00:00Z",
  "created_at": "2025-10-01T10:00:00Z"
}
```

---

## 🛠️ MCP Tools (10 Available)

### 📝 Blog Tools

| Tool | Description |
|------|-------------|
| `get_blog_by_id(blog_id)` | Get detailed blog information |
| `list_blogs_content(limit)` | List all blogs with content |
| `get_blogs_by_keyword(keyword)` | Search blogs by keyword |

### 👥 Member Tools

| Tool | Description |
|------|-------------|
| `get_member_by_id(member_id)` | Get detailed member information |
| `list_members_summary(limit)` | List all team members |
| `get_members_by_keyword(keyword)` | Search members by expertise |

### 🚀 Project Tools

| Tool | Description |
|------|-------------|
| `get_project_by_id(project_id)` | Get detailed project information |
| `list_projects_description(limit)` | List all projects |

### 💬 Chat History Tools

| Tool | Description |
|------|-------------|
| `get_chat_history(user_id)` | Get user's chat history |
| `get_recent_sessions(user_id, n)` | Get recent chat sessions |

---

## 🔌 API Endpoints

### Chat History Management

```bash
# Create chat session
POST /api/session-chat/sessions
{
  "session_id": "unique_id",
  "user_id": "user_123",
  "message": "Hello!",
  "response": "Hi there!",
  "timestamp": "2025-10-01T10:00:00Z"
}

# Get user sessions
GET /api/session-chat/users/{user_id}/sessions?limit=50

# Get chat history (formatted)
GET /api/session-chat/users/{user_id}/history?format=json&limit=10

# Update session response
PATCH /api/session-chat/sessions/{session_id}/response
{
  "response": "Updated response"
}

# Delete user sessions
DELETE /api/session-chat/users/{user_id}/sessions
```

### Health Check

```bash
GET /health
```

---

## 📁 Project Structure

```
PiXerse_LP_Chatbot/
├── core/
│   ├── config/              # Configuration files
│   │   └── server_config.json
│   ├── db/                  # Database layer
│   │   ├── base.py
│   │   ├── meta.py
│   │   ├── mongodb.py
│   │   └── repositories/    # Data access layer
│   │       ├── blog_repository.py
│   │       ├── member_repository.py
│   │       ├── project_repository.py
│   │       └── chat_repository.py
│   ├── schemas/             # Pydantic models
│   │   ├── chatbot_schemas.py
│   │   └── session_chat_schemas.py
│   ├── services/            # Business logic
│   │   ├── MCP_chatbot/
│   │   │   ├── chatbot_service.py
│   │   │   └── mcp_tools.py
│   │   └── History_message/
│   │       └── session_chat_service.py
│   ├── web/                 # Web layer
│   │   ├── api/
│   │   │   ├── MCP_chatbot/
│   │   │   ├── chat_history/
│   │   │   └── router.py
│   │   ├── application.py   # FastAPI app
│   │   └── lifespan.py      # Startup/shutdown
│   └── settings/            # App settings
│       └── base.py
├── Dockerfile               # Production Docker image
├── .dockerignore           # Docker ignore patterns
├── requirements.txt        # Python dependencies
├── env.example             # Environment variables template
├── main.py                 # Application entry point
└── README.md              # This file
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_mcp_tools.py -v

# With coverage
pytest --cov=core tests/

# Test database connections
python -c "from core.db.meta import test_db_connection; import asyncio; asyncio.run(test_db_connection())"
```

---

## 🔧 Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `MONGODB_URL` | MongoDB connection string | Yes | - |
| `MONGODB_DB_NAME` | MongoDB database name | Yes | `PiXerse_ChatBot` |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `SECRET_KEY` | Application secret key | Yes | - |
| `HOST` | Server host | No | `0.0.0.0` |
| `PORT` | Server port (7860 for HF) | No | `7860` |
| `APP_ENV` | Environment (dev/prod) | No | `production` |
| `DEBUG` | Debug mode | No | `false` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

---

## 🚨 Common Issues & Solutions

### 1. Database Connection Failed

**Problem**: `Could not connect to PostgreSQL`

**Solution**:
- Verify `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/db`
- Check database is accessible from your network
- Ensure database credentials are correct

### 2. MongoDB Timeout

**Problem**: `MongoDB connection timeout`

**Solution**:
- Check `MONGODB_URL` is correct
- Verify IP whitelist in MongoDB Atlas (allow `0.0.0.0/0` for testing)
- Check network connectivity

### 3. OpenAI API Error

**Problem**: `Invalid API key`

**Solution**:
- Verify `OPENAI_API_KEY` is correct and active
- Check API key has sufficient credits
- Ensure key starts with `sk-proj-`

### 4. Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port
lsof -i :7860  # or :8000

# Kill process
kill -9 <PID>
```

### 5. Module Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📈 Performance Tips

1. **Use connection pooling** - Already configured in `meta.py`
2. **Enable caching** - Redis integration (optional)
3. **Optimize queries** - Use `include_relations=False` when not needed
4. **Monitor logs** - Check logs for slow queries
5. **Scale horizontally** - Deploy multiple instances behind load balancer

---

## 🔐 Security Best Practices

1. ✅ Never commit `.env` files
2. ✅ Use strong `SECRET_KEY` (generated randomly)
3. ✅ Rotate API keys regularly
4. ✅ Use environment variables for all secrets
5. ✅ Enable HTTPS in production
6. ✅ Implement rate limiting (configured)
7. ✅ Keep dependencies updated
8. ✅ Use non-root user in Docker (configured)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **Model Context Protocol** - Structured AI interactions
- **OpenAI** - AI capabilities
- **Hugging Face** - Deployment platform
- **Strapi** - Database schema inspiration

---

## 📞 Support

- 📧 Email: support@pixerse.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/PiXerse_LP_Chatbot/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/PiXerse_LP_Chatbot/discussions)

---

## 🗺️ Roadmap

- [ ] Add Redis caching
- [ ] Implement WebSocket support
- [ ] Add multilingual support
- [ ] Integration with more AI models
- [ ] Advanced analytics dashboard
- [ ] GraphQL API
- [ ] Kubernetes deployment configs

---

**Made with ❤️ by PiXerse Team** 🎯

**Ready to deploy to Hugging Face Spaces!** 🚀
