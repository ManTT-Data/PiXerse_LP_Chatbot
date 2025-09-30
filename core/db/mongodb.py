"""
MongoDB async connection and utilities for chat history
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import Optional
import logging

from core.settings.base import settings

logger = logging.getLogger(__name__)

# MongoDB client instance
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


def get_mongodb_client() -> AsyncIOMotorClient:
    """Get MongoDB client instance"""
    global _client
    
    if _client is None:
        mongo_url = settings.MONGODB_URL.get_secret_value()
        if not mongo_url:
            raise ValueError("MONGODB_URL is not configured in environment")
        
        # Add tlsAllowInvalidCertificates for macOS SSL issues
        if 'tlsAllowInvalidCertificates' not in mongo_url:
            separator = '&' if '?' in mongo_url else '?'
            mongo_url = f"{mongo_url}{separator}tlsAllowInvalidCertificates=true"
        
        _client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT or 5000
        )
        logger.info("MongoDB client initialized")
    
    return _client


def get_mongodb_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance"""
    global _database
    
    if _database is None:
        client = get_mongodb_client()
        db_name = settings.MONGODB_DB_NAME or "PiXerse_ChatBot"
        _database = client[db_name]
        logger.info(f"MongoDB database '{db_name}' initialized")
    
    return _database


def get_chat_collection() -> AsyncIOMotorCollection:
    """Get chat sessions collection"""
    db = get_mongodb_database()
    collection_name = settings.MONGODB_COLLECTION_NAME or "chat_sessions"
    return db[collection_name]


async def test_mongodb_connection() -> bool:
    """Test MongoDB connection"""
    try:
        client = get_mongodb_client()
        # Issue a ping to confirm connection
        await client.admin.command('ping')
        logger.info("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False


async def close_mongodb_connection():
    """Close MongoDB connection"""
    global _client, _database
    
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")
