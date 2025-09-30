from fastapi.routing import APIRouter

from core.web.api import MCP_chatbot
from core.web.api.chat_history import views as chat_history

api_router = APIRouter()
api_router.include_router(MCP_chatbot.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(chat_history.router)