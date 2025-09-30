from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from core.services.MCP_chatbot.chatbot_service import MCP_ChatBot
from core.settings import settings
from core.db.meta import create_tables, test_db_connection
from core.db.mongodb import test_mongodb_connection, close_mongodb_connection

@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    app.middleware_stack = None

    # Test PostgreSQL database connection
    print("🔍 Testing PostgreSQL connection...")
    await test_db_connection()
    
    # Create database tables
    print("🏗️ Creating database tables...")
    await create_tables()
    
    # Test MongoDB connection
    print("🔍 Testing MongoDB connection...")
    await test_mongodb_connection()

    # Setup MCP Chatbot
    print("🤖 Setting up MCP Chatbot...")
    global chatbot
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_servers()
    app.state.chatbot = chatbot

    app.middleware_stack = app.build_middleware_stack()
    print("✅ Application startup completed!")

    yield
    
    # Cleanup
    print("🔄 Closing MongoDB connection...")
    await close_mongodb_connection()
    print("🔄 Application shutdown completed!")