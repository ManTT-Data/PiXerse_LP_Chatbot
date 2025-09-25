from fastapi.routing import APIRouter

from core.web.api import MCP_chatbot

api_router = APIRouter()
api_router.include_router(MCP_chatbot.router, prefix="/mcp", tags=["mcp"])