from typing import Any, Dict

from pydantic import BaseModel, Field


class ChatbotQuery(BaseModel):
    query: str = Field(..., description="User query")


class ChatbotResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    token_usage: int = Field(..., description="Number of tokens used")
    tools_used: list = Field(..., description="List of tools used")
    tools_response: list = Field(..., description="Tool responses")


class ToolResponse(BaseModel):
    tool_name: str
    args: Dict[str, Any]
    success: bool
    content: str