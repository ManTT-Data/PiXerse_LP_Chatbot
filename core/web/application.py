from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import openai
import json
import uuid
from core.settings.base import settings
from core.services.mcp_tools import get_mcp_tools
from core.db.database import create_tables

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: Optional[list] = None
    mcp_tools_used: Optional[list] = None
    tokens_used: Optional[dict] = None
    tool_execution_details: Optional[dict] = None

# Create FastAPI application
app = FastAPI(
    title="PiXerse Team MCP Chatbot API",
    description="API for PiXerse Team introduction chatbot using Model Context Protocol",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.openai_api_key)

# In-memory conversation storage (use Redis in production)
conversations = {}

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    # Create database tables
    try:
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Failed to create database tables: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML response"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PiXerse Team MCP Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .info { background: #e8f4f8; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .endpoints { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            .chat-demo { background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 PiXerse Team MCP Chatbot API</h1>
            
            <div class="info">
                <h3>Giới thiệu</h3>
                <p>Chào mừng bạn đến với API chatbot giới thiệu PiXerse Team! 
                Đây là hệ thống chatbot sử dụng Model Context Protocol (MCP) để cung cấp thông tin về:</p>
                <ul>
                    <li>✨ <strong>Thành viên team</strong> - Thông tin về các thành viên và kỹ năng</li>
                    <li>🚀 <strong>Dự án</strong> - Các dự án đã và đang phát triển</li>
                    <li>📝 <strong>Blog</strong> - Bài viết và chia sẻ kinh nghiệm</li>
                    <li>🖼️ <strong>Assets</strong> - Hình ảnh, video và tài nguyên đa phương tiện</li>
                </ul>
            </div>
            
            <div class="endpoints">
                <h3>API Documentation</h3>
                <ul>
                    <li>📚 <a href="/docs">Swagger UI Documentation</a></li>
                    <li>📖 <a href="/redoc">ReDoc Documentation</a></li>
                    <li>💬 <a href="/chat">Chat Endpoint</a></li>
                    <li>🔍 <a href="/health">Health Check</a></li>
                </ul>
            </div>
            
            <div class="chat-demo">
                <h3>Demo Chat Request</h3>
                <p>Để chat với bot, gửi POST request đến <code>/chat</code> với body:</p>
                <pre><code>{
    "message": "Hãy giới thiệu về PiXerse Team",
    "conversation_id": "optional-conversation-id"
}</code></pre>
                
                <h4>Response Format</h4>
                <p>API sẽ trả về:</p>
                <pre><code>{
    "response": "Câu trả lời từ AI",
    "conversation_id": "unique-conversation-id",
    "sources": ["Database dự án PiXerse", "Database thành viên team"],
    "mcp_tools_used": ["projects_description", "members_description"],
    "tokens_used": {
        "prompt_tokens": 245,
        "completion_tokens": 150,
        "total_tokens": 395,
        "model": "gpt-3.5-turbo"
    }
}</code></pre>
            </div>
            
            <div class="info">
                <h3>MCP Tools Available</h3>
                <p>Hệ thống sử dụng 12 MCP tools để truy xuất dữ liệu:</p>
                <ul>
                    <li>🏗️ <strong>Projects:</strong> projects_description, projects_list, projects_get</li>
                    <li>👥 <strong>Members:</strong> members_description, members_search, members_get</li>
                    <li>📝 <strong>Blogs:</strong> blogs_description, blogs_list, blogs_get</li>
                    <li>🖼️ <strong>Assets:</strong> assets_description, assets_search, assets_get</li>
                </ul>
                <p>Thông tin về tools đã sử dụng sẽ được hiển thị trong <code>mcp_tools_used</code> và <code>tool_execution_details</code>.</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_relevant_context(message: str) -> tuple[str, list, dict]:
    """Get relevant context for the message using MCP tools and return used tools with details"""
    tools = get_mcp_tools()
    context_parts = []
    used_tools = []
    tool_details = {}
    
    try:
        message_lower = message.lower()
        
        # Check if asking about projects
        if any(keyword in message_lower for keyword in ["dự án", "project", "sản phẩm", "app", "ứng dụng"]):
            projects = tools.projects_description()
            if projects:
                context_parts.append("THÔNG TIN DỰ ÁN:")
                for project in projects[:5]:  # Limit to 5 projects
                    context_parts.append(f"- {project['project_name']}: {project['project_description']}")
                used_tools.append("projects_description")
                tool_details["projects_description"] = {
                    "description": "Lấy danh sách và mô tả các dự án",
                    "results_count": len(projects),
                    "data_source": "Database bảng projects"
                }
        
        # Check if asking about members
        if any(keyword in message_lower for keyword in ["thành viên", "member", "người", "team", "ai là"]):
            members = tools.members_description()
            if members:
                context_parts.append("THÔNG TIN THÀNH VIÊN:")
                for member in members[:5]:  # Limit to 5 members
                    context_parts.append(f"- {member['member_name']} ({member['member_role']}): {member['summary']}")
                used_tools.append("members_description")
                tool_details["members_description"] = {
                    "description": "Lấy danh sách và thông tin thành viên team",
                    "results_count": len(members),
                    "data_source": "Database bảng members"
                }
        
        # Check if asking about blogs
        if any(keyword in message_lower for keyword in ["blog", "bài viết", "article", "tutorial", "chia sẻ"]):
            blogs = tools.blogs_description(limit=5)
            if blogs:
                context_parts.append("THÔNG TIN BLOG:")
                for blog in blogs:
                    context_parts.append(f"- {blog['blog_title']}: {blog['preview'][:100]}...")
                used_tools.append("blogs_description")
                tool_details["blogs_description"] = {
                    "description": "Lấy danh sách bài viết blog",
                    "results_count": len(blogs),
                    "data_source": "Database bảng blogs"
                }
        
        # Check if asking about assets
        if any(keyword in message_lower for keyword in ["hình ảnh", "ảnh", "video", "asset", "tài liệu", "file"]):
            assets = tools.assets_description()
            if assets:
                context_parts.append("THÔNG TIN TÀI NGUYÊN:")
                for asset in assets[:3]:  # Limit to 3 assets
                    context_parts.append(f"- {asset['filename']}: {asset.get('description', 'Không có mô tả')}")
                used_tools.append("assets_description")
                tool_details["assets_description"] = {
                    "description": "Lấy danh sách tài nguyên đa phương tiện",
                    "results_count": len(assets),
                    "data_source": "Database bảng assets"
                }
        
        # If no specific context found, get general overview
        if not context_parts:
            projects = tools.projects_description()
            members = tools.members_description()
            
            if projects:
                context_parts.append(f"PiXerse Team có {len(projects)} dự án:")
                for project in projects[:3]:
                    context_parts.append(f"- {project['project_name']}")
                used_tools.append("projects_description")
                tool_details["projects_description"] = {
                    "description": "Lấy tổng quan dự án (fallback)",
                    "results_count": len(projects),
                    "data_source": "Database bảng projects"
                }
            
            if members:
                context_parts.append(f"Team có {len(members)} thành viên:")
                for member in members[:3]:
                    context_parts.append(f"- {member['member_name']} ({member['member_role']})")
                used_tools.append("members_description")
                tool_details["members_description"] = {
                    "description": "Lấy tổng quan thành viên (fallback)",
                    "results_count": len(members),
                    "data_source": "Database bảng members"
                }
    
    except Exception as e:
        print(f"Error getting context: {e}")
        context_parts.append("Xin lỗi, tôi gặp sự cố khi truy xuất thông tin.")
        tool_details["error"] = {
            "description": "Lỗi khi thực thi MCP tools",
            "error_message": str(e)
        }
    
    finally:
        try:
            tools.db.close()
        except:
            pass
    
    return "\n".join(context_parts), used_tools, tool_details

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with the PiXerse Team chatbot"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Initialize conversation if new
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Get relevant context using MCP tools
        context, used_tools, tool_details = get_relevant_context(request.message)
        
        # Prepare system prompt
        system_prompt = """
Bạn là trợ lý AI chuyên giới thiệu về PiXerse Team. PiXerse là một team phát triển sản phẩm công nghệ sáng tạo.

Nhiệm vụ của bạn:
1. Giới thiệu các thành viên trong team (members)
2. Chia sẻ thông tin về các dự án (projects) mà team đã và đang thực hiện
3. Cung cấp thông tin về các bài viết blog của team
4. Trả lời các câu hỏi về kinh nghiệm, kỹ năng, và hoạt động của team

Quy tắc trả lời:
- Sử dụng tiếng Việt một cách tự nhiên và thân thiện
- Cung cấp thông tin chính xác dựa trên dữ liệu có sẵn
- Nếu không có thông tin cụ thể, hãy nói rõ và đề xuất cách liên hệ
- Luôn nhiệt tình và tích cực trong việc giới thiệu team
- Có thể đề xuất thông tin liên quan khác mà người dùng có thể quan tâm

Khi được hỏi về thành viên, hãy bao gồm: tên, vai trò, kỹ năng chính.
Khi được hỏi về dự án, hãy bao gồm: tên dự án, mô tả, và thành viên tham gia.
Khi được hỏi về blog, hãy bao gồm: tiêu đề, tóm tắt, và tác giả.
"""
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add context if available
        if context:
            messages.append({
                "role": "system", 
                "content": f"THÔNG TIN LIÊN QUAN ĐỂ TRẢ LỜI:\n{context}"
            })
        
        # Add conversation history (last 6 messages)
        messages.extend(conversations[conversation_id][-6:])
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Extract token usage information
        tokens_info = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "model": "gpt-4o-mini"
        }
        
        # Save to conversation history
        conversations[conversation_id].extend([
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Generate sources info
        sources = []
        if "THÔNG TIN DỰ ÁN:" in context:
            sources.append("Database dự án PiXerse")
        if "THÔNG TIN THÀNH VIÊN:" in context:
            sources.append("Database thành viên team")
        if "THÔNG TIN BLOG:" in context:
            sources.append("Database bài viết blog")
        
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            sources=sources,
            mcp_tools_used=used_tools,
            tokens_used=tokens_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Xin lỗi, tôi gặp sự cố khi xử lý câu hỏi của bạn: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PiXerse Team MCP Chatbot",
        "version": "1.0.0"
    }
