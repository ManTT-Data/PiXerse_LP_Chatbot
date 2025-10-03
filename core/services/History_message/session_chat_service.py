"""
Chat Service - Business logic for chat operations
"""

from typing import List, Optional
import logging

from core.db.repositories.chat_repository import ChatRepository
from core.schemas.session_chat_schemas import ChatSessionCreate

logger = logging.getLogger(__name__)


class ChatService:
    """Service layer for chat operations"""
    
    @staticmethod
    async def create_session(session_data: ChatSessionCreate) -> dict:
        """
        Create a new chat session
        
        Args:
            session_data: Chat session data
            
        Returns:
            dict: Result with acknowledged status and session info
        """
        try:
            result = await ChatRepository.save_session(session_data)
            logger.info(f"Chat session created: {session_data.session_id}")
            return result
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise
    
    @staticmethod
    async def get_session_by_id(session_id: str) -> Optional[dict]:
        """
        Get a specific chat session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict: Session data or None if not found
        """
        try:
            session = await ChatRepository.get_session_by_id(session_id)
            if session:
                logger.debug(f"Retrieved session: {session_id}")
            return session
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            raise
    
    @staticmethod
    async def update_session_response(session_id: str, response: str) -> bool:
        """
        Update bot response for a session
        
        Args:
            session_id: Session identifier
            response: Bot response text
            
        Returns:
            bool: True if updated successfully
        """
        try:
            success = await ChatRepository.update_session_response(session_id, response)
            if success:
                logger.info(f"Session response updated: {session_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating session response: {e}")
            raise
    
    @staticmethod
    async def get_user_sessions(
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[dict]:
        """
        Get all chat sessions for a specific user
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions
            skip: Number of sessions to skip (pagination)
            
        Returns:
            List[dict]: List of user sessions
        """
        try:
            sessions = await ChatRepository.get_user_sessions(user_id, limit, skip)
            logger.debug(f"Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            raise
    
    @staticmethod
    async def get_user_chat_history(
        user_id: str,
        limit: int = 10,
        format: str = "text"
    ) -> dict:
        """
        Get formatted chat history for a user
        
        Args:
            user_id: User identifier
            limit: Maximum messages to include
            format: Response format (text or json)
            
        Returns:
            dict: Formatted chat history
        """
        try:
            if format == "text":
                history = await ChatRepository.get_chat_history(user_id, limit)
                return {
                    "user_id": user_id,
                    "format": "text",
                    "history": history
                }
            else:  # json format
                sessions = await ChatRepository.get_user_sessions(user_id, limit=limit)
                history_text = await ChatRepository.get_chat_history(user_id, limit)
                return {
                    "user_id": user_id,
                    "format": "json",
                    "total_sessions": len(sessions),
                    "sessions": sessions,
                    "formatted_history": history_text
                }
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            raise
    
    @staticmethod
    async def get_recent_sessions(
        user_id: str,
        n: int = 3
    ) -> dict:
        """
        Get n most recent sessions for a user
        
        Args:
            user_id: User identifier
            n: Number of sessions to retrieve
            
        Returns:
            dict: Recent sessions info
        """
        try:
            sessions = await ChatRepository.get_recent_sessions(user_id, n)
            return {
                "user_id": user_id,
                "count": len(sessions),
                "sessions": sessions
            }
        except Exception as e:
            logger.error(f"Error getting recent sessions: {e}")
            raise
    
    @staticmethod
    async def delete_user_sessions(user_id: str) -> dict:
        """
        Delete all chat sessions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            dict: Deletion result with count
        """
        try:
            deleted_count = await ChatRepository.delete_user_sessions(user_id)
            logger.warning(f"Deleted {deleted_count} sessions for user {user_id}")
            return {
                "message": f"Deleted {deleted_count} sessions for user {user_id}",
                "deleted_count": deleted_count
            }
        except Exception as e:
            logger.error(f"Error deleting user sessions: {e}")
            raise

