# PiXerse Team MCP Chatbot

Hệ thống chatbot thông minh sử dụng Model Context Protocol (MCP) để giới thiệu về PiXerse Team, dự án, thành viên và blog posts.

## 🚀 Tính năng chính

- **MCP Tools Integration**: 12 tools chuyên biệt để query dữ liệu team
- **OpenAI Integration**: Sử dụng GPT-4o-mini cho natural language processing
- **FastAPI Web Interface**: REST API và web interface đơn giản
- **PostgreSQL Database**: Lưu trữ thông tin projects, members, blogs, và assets
- **Scalable Architecture**: Microservices-ready với Docker support

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │────│   FastAPI App   │────│  PostgreSQL DB  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                       ┌─────────────────┐
                       │   MCP Server    │
                       └─────────────────┘
                               │
                       ┌─────────────────┐
                       │   OpenAI API    │
                       └─────────────────┘
```

## 📦 Cài đặt

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- OpenAI API Key

### 1. Clone repository

```bash
git clone <repository-url>
cd MCP\ LP\ PiX
```

### 2. Tạo virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Thiết lập database

```bash
# Tạo PostgreSQL database
createdb pixerse_mcp_db

# Hoặc sử dụng psql
psql -U postgres -c "CREATE DATABASE pixerse_mcp_db;"
```

### 5. Cấu hình environment variables

Tạo file `.env`:

```env
# Database Configuration
DATABASE_URL=

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 6. Tạo sample data

```bash
python scripts/create_sample_data.py
```

## 🚀 Chạy ứng dụng

### Development Mode

```bash
python main.py
```

Hoặc sử dụng uvicorn trực tiếp:

```bash
uvicorn core.web.application:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode

```bash
uvicorn core.web.application:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
# Build image
docker build -t pixerse-mcp-chatbot .

# Run container
docker run -p 8000:8000 --env-file .env pixerse-mcp-chatbot
```

## 🔧 API Usage

### Chat Endpoint

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Giới thiệu về team PiXerse",
    "conversation_id": "optional-conversation-id"
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

### Web Interface

Truy cập: `http://localhost:8000`

## 🛠️ MCP Tools

Hệ thống cung cấp 12 MCP tools để query dữ liệu:

### Projects
- `projects_description`: Mô tả tổng quan về projects
- `projects_get`: Lấy thông tin chi tiết project theo ID
- `projects_list`: Liệt kê tất cả projects

### Members
- `members_description`: Mô tả tổng quan về team members
- `members_get`: Lấy thông tin member theo ID
- `members_search`: Tìm kiếm members theo tên hoặc role

### Blogs
- `blogs_description`: Mô tả tổng quan về blog system
- `blogs_get`: Lấy nội dung blog theo ID
- `blogs_list`: Liệt kê blogs với filters

### Assets
- `assets_description`: Mô tả tổng quan về asset management
- `assets_get`: Lấy thông tin asset theo ID
- `assets_search`: Tìm kiếm assets theo filename hoặc type

## 📊 Database Schema

### Bảng chính

```sql
-- Projects
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    project_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Members
CREATE TABLE members (
    member_id SERIAL PRIMARY KEY,
    member_name VARCHAR(255) NOT NULL,
    member_role VARCHAR(255),
    team_type VARCHAR(100),
    summary TEXT,
    avatar_url VARCHAR(500),
    project_id INTEGER REFERENCES projects(project_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blogs
CREATE TABLE blogs (
    blog_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    blog_title VARCHAR(500) NOT NULL,
    blog_content TEXT,
    author_id INTEGER REFERENCES members(member_id),
    category VARCHAR(100),
    tags JSON,
    featured_image VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assets
CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    cloudinary_url VARCHAR(500),
    asset_type VARCHAR(50),
    file_size BIGINT,
    mime_type VARCHAR(100),
    youtube_video_id VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blog Assets (Many-to-Many)
CREATE TABLE blog_assets (
    blog_id INTEGER REFERENCES blogs(blog_id),
    asset_id INTEGER REFERENCES assets(asset_id),
    PRIMARY KEY (blog_id, asset_id)
);
```

## 🎯 Sample Data

Hệ thống đi kèm với sample data phong phú:

- **4 Projects**: E-commerce Platform, Healthcare Dashboard, AI Content Generator, Blockchain Voting
- **6 Team Members**: Từ các roles khác nhau (Tech, Design, Marketing)
- **5 Blog Posts**: Technical tutorials và showcases
- **5 Assets**: Images, videos, và YouTube links

## 🧪 Testing

### Run Tests

```bash
# Unit tests
pytest tests/

# Specific test file
pytest tests/test_mcp_tools.py -v

# With coverage
pytest --cov=core tests/
```

### Manual Testing

```bash
# Test MCP tools directly
python -c "
from core.services.mcp_tools import MCPTools
from core.db.database import SessionLocal

db = SessionLocal()
tools = MCPTools(db)
print(tools.projects_list())
db.close()
"
```

## 📝 Development

### Project Structure

```
core/
├── config/          # Configuration files
├── db/             # Database setup và connection
├── schemas/        # SQLAlchemy models
├── services/       # Business logic và MCP tools
├── settings/       # Application settings
└── web/           # FastAPI application
    └── api/       # API routes
        └── MCP_chatbot/  # Chat-specific endpoints

scripts/           # Utility scripts
deploy/           # Deployment configurations
test/             # Test files
```

### Adding New MCP Tools

1. Thêm method vào `MCPTools` class trong `core/services/mcp_tools.py`
2. Update `list_tools()` method để include tool mới
3. Update `call_tool()` method để handle tool call
4. Thêm tests trong `tests/test_mcp_tools.py`

### Code Style

```bash
# Format code
black core/ scripts/ tests/

# Lint
flake8 core/ scripts/ tests/

# Type checking
mypy core/
```

## 🚢 Deployment

### Docker Deployment

```bash
# Build và push image
docker build -t pixerse-mcp-chatbot:latest .
docker tag pixerse-mcp-chatbot:latest your-registry/pixerse-mcp-chatbot:latest
docker push your-registry/pixerse-mcp-chatbot:latest

# Deploy với docker-compose
docker-compose up -d
```

### Cloud Deployment

#### AWS ECS
```bash
# Tạo task definition
aws ecs register-task-definition --cli-input-json file://deploy/ecs-task-definition.json

# Update service
aws ecs update-service --cluster pixerse-cluster --service pixerse-mcp-chatbot --task-definition pixerse-mcp-chatbot:1
```

#### Kubernetes
```bash
# Apply manifests
kubectl apply -f deploy/k8s/
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL service
   pg_ctl status
   
   # Verify database exists
   psql -l | grep pixerse
   ```

2. **OpenAI API Errors**
   ```bash
   # Test API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

3. **MCP Tools Not Working**
   ```bash
   # Check database data
   python -c "
   from core.db.database import SessionLocal
   from core.schemas.models import Projects
   db = SessionLocal()
   print(f'Projects count: {db.query(Projects).count()}')
   db.close()
   "
   ```

### Debug Mode

Set `DEBUG=True` trong `.env` để enable verbose logging:

```bash
export DEBUG=True
python main.py
```

## 📚 API Documentation

Khi chạy server, truy cập:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📄 License

MIT License - xem file `LICENSE` để biết thêm chi tiết.

## 📞 Support

- **Email**: support@pixerse.com
- **Documentation**: [docs.pixerse.com](https://docs.pixerse.com)
- **Issues**: [GitHub Issues](https://github.com/pixerse/mcp-chatbot/issues)

---

Made with ❤️ by PiXerse Team
