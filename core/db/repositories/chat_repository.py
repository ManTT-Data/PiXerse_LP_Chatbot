"""
Repository for chat history operations with MongoDB
"""

from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
import logging

from core.db.mongodb.mongodb import get_chat_collection
from core.schemas.session_chat_schemas import ChatSession, ChatSessionCreate

logger = logging.getLogger(__name__)


class ChatRepository:
    """Repository for chat operations"""
    
    @staticmethod
    def _get_collection() -> AsyncIOMotorCollection:
        """Get chat collection"""
        return get_chat_collection()
    
    @staticmethod
    async def save_session(session_data: ChatSessionCreate) -> dict:
        """Save a new chat session"""
        try:
            collection = ChatRepository._get_collection()
            
            # Convert to dict and ensure timestamps
            session_dict = session_data.model_dump()
            now = datetime.utcnow()
            if 'timestamp' not in session_dict or session_dict['timestamp'] is None:
                session_dict['timestamp'] = now
            session_dict['created_at'] = now
            
            result = await collection.insert_one(session_dict)
            logger.info(f"Session saved with ID: {result.inserted_id}")
            
            return {
                "acknowledged": result.acknowledged,
                "inserted_id": str(result.inserted_id),
                "session_data": session_dict
            }
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            raise
    
    @staticmethod
    async def update_session_response(session_id: str, response: str) -> bool:
        """Update a session with bot response"""
        try:
            collection = ChatRepository._get_collection()
            
            # Check if session exists
            existing = await collection.find_one({"session_id": session_id})
            if not existing:
                logger.warning(f"No session found with ID: {session_id}")
                return False
            
            result = await collection.update_one(
                {"session_id": session_id},
                {"$set": {"response": response}}
            )
            
            logger.info(f"Session {session_id} updated with response")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating session response: {e}")
            raise
    
    @staticmethod
    async def get_session_by_id(session_id: str) -> Optional[dict]:
        """Get a session by session_id"""
        try:
            collection = ChatRepository._get_collection()
            session = await collection.find_one({"session_id": session_id})
            
            if session:
                session['_id'] = str(session['_id'])
            
            return session
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    @staticmethod
    async def get_user_sessions(
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[dict]:
        """Get sessions for a specific user"""
        try:
            collection = ChatRepository._get_collection()
            
            query = {"user_id": user_id}
            
            cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
            sessions = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for session in sessions:
                session['_id'] = str(session['_id'])
            
            logger.debug(f"Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    @staticmethod
    async def get_chat_history(user_id: str, limit: int = 10) -> str:
        """
        Get formatted chat history for a user
        Returns formatted string: User: ... Bot: ...
        """
        try:
            collection = ChatRepository._get_collection()
            
            # Get recent sessions sorted by timestamp
            cursor = collection.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(limit)
            
            sessions = await cursor.to_list(length=limit)
            
            # Reverse to get chronological order
            sessions.reverse()
            
            if not sessions:
                logger.info(f"No chat history found for user {user_id}")
                return ""
            
            # Format conversations
            conversation_lines = []
            for session in sessions:
                message = session.get("message", "")
                response = session.get("response", "")
                
                if message:
                    conversation_lines.append(f"User: {message}")
                    if response:
                        conversation_lines.append(f"Bot: {response}")
            
            result = "\n".join(conversation_lines)
            logger.debug(f"Formatted chat history for user {user_id}: {len(conversation_lines)} lines")
            return result
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return ""
    
    @staticmethod
    async def get_recent_sessions(user_id: str, n: int = 3) -> List[dict]:
        """Get n most recent sessions"""
        try:
            collection = ChatRepository._get_collection()
            
            cursor = collection.find(
                {"user_id": user_id},
                {"_id": 0, "message": 1, "response": 1, "timestamp": 1}
            ).sort("timestamp", -1).limit(n)
            
            sessions = await cursor.to_list(length=n)
            logger.debug(f"Retrieved {len(sessions)} recent sessions for user {user_id}")
            return sessions
        except Exception as e:
            logger.error(f"Error getting recent sessions: {e}")
            return []
    
    @staticmethod
    async def delete_user_sessions(user_id: str) -> int:
        """Delete all sessions for a user (for testing/cleanup)"""
        try:
            collection = ChatRepository._get_collection()
            result = await collection.delete_many({"user_id": user_id})
            logger.info(f"Deleted {result.deleted_count} sessions for user {user_id}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting user sessions: {e}")
            return 0
