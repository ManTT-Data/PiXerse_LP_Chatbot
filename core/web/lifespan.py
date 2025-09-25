from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from core.services.MCP_chatbot.chatbot_service import MCP_ChatBot
from core.settings import settings

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

    # Setup MCP Chatbot
    global chatbot
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_servers()
    app.state.chatbot = chatbot

    # await _create_tables()
    app.middleware_stack = app.build_middleware_stack()

    yield