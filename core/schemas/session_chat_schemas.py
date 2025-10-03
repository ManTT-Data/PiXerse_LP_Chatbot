"""
Pydantic schemas for chat history
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")


class ChatSession(BaseModel):
    """Chat session document"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    username: Optional[str] = Field(default=None, description="Username")
    first_name: Optional[str] = Field(default=None, description="User first name")
    last_name: Optional[str] = Field(default=None, description="User last name")
    message: str = Field(..., description="User message")
    response: Optional[str] = Field(default=None, description="Bot response")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "user_id": "user_456",
                "username": "john_doe",
                "message": "Hello, how can I help?",
                "response": "I'm here to assist you!",
                "timestamp": "2025-09-30T10:00:00Z"
            }
        }


class ChatSessionCreate(BaseModel):
    """Schema for creating a chat session"""
    session_id: str
    user_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    message: str
    response: Optional[str] = None
    timestamp: Optional[datetime] = None


class ChatSessionResponse(BaseModel):
    """Response schema for chat session"""
    acknowledged: bool
    inserted_id: Optional[str] = None
    session_data: Optional[ChatSession] = None


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history"""
    user_id: str
    total_sessions: int
    sessions: List[ChatSession]
    formatted_history: Optional[str] = None


class UpdateResponseRequest(BaseModel):
    """Request to update session response"""
    response: str = Field(..., description="Bot response to update")
