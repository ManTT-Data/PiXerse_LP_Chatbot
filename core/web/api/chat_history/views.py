"""
API endpoints for chat history management
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List
import logging

from core.schemas.chat_schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    UpdateResponseRequest
)
from core.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat-history", tags=["Chat History"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_chat_session(session: ChatSessionCreate):
    """
    Create a new chat session
    
    - **session_id**: Unique session identifier
    - **user_id**: User identifier
    - **message**: User message
    - **response**: Bot response (optional)
    - **timestamp**: Message timestamp (optional, auto-generated if not provided)
    """
    try:
        result = await ChatService.create_session(session)
        return result
    except Exception as e:
        logger.error(f"Error in create_chat_session endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_chat_session(
    session_id: str = Path(..., description="Session ID to retrieve")
):
    """
    Get a specific chat session by ID
    """
    try:
        session = await ChatService.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_chat_session endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")


@router.patch("/sessions/{session_id}/response")
async def update_session_response(
    session_id: str = Path(..., description="Session ID to update"),
    request: UpdateResponseRequest = ...
):
    """
    Update bot response for a session
    """
    try:
        success = await ChatService.update_session_response(session_id, request.response)
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return {"message": "Response updated successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_session_response endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update response: {str(e)}")


@router.get("/users/{user_id}/sessions", response_model=List[dict])
async def get_user_sessions(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of sessions to retrieve"),
    skip: int = Query(0, ge=0, description="Number of sessions to skip")
):
    """
    Get all chat sessions for a specific user
    
    - **user_id**: User identifier
    - **limit**: Maximum number of sessions (1-100, default: 50)
    - **skip**: Number of sessions to skip (for pagination)
    """
    try:
        sessions = await ChatService.get_user_sessions(user_id, limit, skip)
        return sessions
    except Exception as e:
        logger.error(f"Error in get_user_sessions endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")


@router.get("/users/{user_id}/history")
async def get_user_chat_history(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(10, ge=1, le=50, description="Maximum messages to include"),
    format: str = Query("text", regex="^(text|json)$", description="Response format: text or json")
):
    """
    Get formatted chat history for a user
    
    - **user_id**: User identifier
    - **limit**: Maximum number of messages (default: 10)
    - **format**: Response format (text or json)
    
    Returns conversation in format:
    ```
    User: message
    Bot: response
    ```
    """
    try:
        result = await ChatService.get_user_chat_history(user_id, limit, format)
        return result
    except Exception as e:
        logger.error(f"Error in get_user_chat_history endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/users/{user_id}/recent")
async def get_recent_sessions(
    user_id: str = Path(..., description="User ID"),
    n: int = Query(3, ge=1, le=10, description="Number of recent sessions")
):
    """
    Get n most recent sessions
    
    - **user_id**: User identifier
    - **n**: Number of sessions (1-10, default: 3)
    """
    try:
        result = await ChatService.get_recent_sessions(user_id, n)
        return result
    except Exception as e:
        logger.error(f"Error in get_recent_sessions endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")


@router.delete("/users/{user_id}/sessions")
async def delete_user_sessions(
    user_id: str = Path(..., description="User ID to delete sessions for")
):
    """
    Delete all chat sessions for a user (use with caution!)
    """
    try:
        result = await ChatService.delete_user_sessions(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete_user_sessions endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete sessions: {str(e)}")
