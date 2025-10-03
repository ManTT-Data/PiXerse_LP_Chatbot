import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI as OpenAI

from core.constants.openai_constants import (
    OPENAI_MAX_TOKENS,
    OPENAI_TEMPERATURE,
    SYSTEM_PROMPT,
)
from core.log_handler import logger
from core.schemas.chatbot_schemas import ToolResponse
from core.services.History_message.session_chat_service import ChatService
from core.settings.base import settings
import uuid
from datetime import datetime
from core.schemas.session_chat_schemas import ChatSessionCreate


class MCP_ChatBot:
    def __init__(self):
        # Manage the lifecycle of multiple async contexts
        self.exit_stack = AsyncExitStack()

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())

        self.available_mcp_tools: List[Dict[str, Any]] = []
        # Store the tool name → ClientSession mapping for invoking tools later
        self.tool_sessions: Dict[str, ClientSession] = {}

    async def connect_to_server(
        self,
        server_name: str,
        server_config: Dict[str, Any],
    ) -> None:
        """
        Connects to a single MCP server via stdio and registers available tools.
        """
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params),
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write),
            )
            await session.initialize()

            await self._register_tools(session)

            print(f"✅ Connected to MCP servers successfully.")

        except Exception as e:
            print(f"❌ Error connecting to MCP server '{server_name}': {e}")
            logger.error(f"❌ Error connecting to MCP server '{server_name}': {e}")

    async def connect_to_servers(self) -> None:
        """
        Loads the server config file and connects to all defined MCP servers.
        """
        try:
            config_path = settings.mcp_server_config_path

            if not config_path.exists():
                print(f"server_config.json not found at {config_path}")
                raise FileNotFoundError(
                    f"server_config.json not found at {config_path}",
                )

            # Load config file containing multiple MCP server definitions
            with config_path.open("r", encoding="utf-8") as file:
                config_data = json.load(file)

            servers = config_data.get("mcpServers", {})

            for name, cfg in servers.items():
                print(name, cfg)
                await self.connect_to_server(name, cfg)

        except Exception as e:
            logger.error(f"❌ Failed to load MCP server config: {e}")
            raise

    async def process_query(
        self,
        query: str,
        user_id: str = None,
        include_history: bool = True,
        history_limit: int = 10,
    ) -> Tuple[str, int, List[str], List[Dict[str, Any]]]:
        """
        Args:
            query (str): User's query/message
            user_id (str, optional): User ID to retrieve chat history
            include_history (bool): Whether to include chat history in context
            history_limit (int): Maximum number of historical messages to include
        """

        session_id = f"session_{uuid.uuid4().hex}"
        
        # Save user message to database first
        try:
            session_data = ChatSessionCreate(
                session_id=session_id,
                user_id=user_id,
                message=query,
                response=None,  # Will be updated after getting bot response
                timestamp=datetime.utcnow()
            )
            
            await ChatService.create_session(session_data)
            logger.info(f"Saved user message for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save user message: {e}")

        # Initialize chat messages with system prompt
        chatbot_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
        ]
        
        # Add chat history if user_id is provided and include_history is True
        if user_id and include_history:
            try:
                chat_history = await ChatService.get_user_chat_history(
                    user_id=user_id,
                    limit=history_limit,
                    format="text"
                )
                
                history_text = chat_history.get("history", "")
                if history_text:
                    # Add history as context in system message
                    chatbot_messages.append({
                        "role": "system",
                        "content": f"Previous conversation history:\n{history_text}\n\nPlease consider this context when responding to the current query."
                    })
                    logger.info(f"Added chat history for user {user_id} ({len(history_text)} characters)")
                else:
                    logger.info(f"No chat history found for user {user_id}")
                    
            except Exception as e:
                logger.warning(f"Failed to retrieve chat history for user {user_id}: {e}")
                # Continue without history if there's an error
        
        # Add current user query
        chatbot_messages.append({"role": "user", "content": query})
        session_chat = [{"role": "user", "content": query}]
        chatbot_token_usage = 0
        mcp_tools_used = []
        mcp_tools_response = []

        while True:
            # Call OpenAI Chat API with available tools
            chatbot_response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE,
                timeout=settings.OPENAI_TIMEOUT,
                messages=chatbot_messages,
                tools=self.available_mcp_tools,
                tool_choice="auto",
            )

            if chatbot_response.usage:
                chatbot_token_usage += chatbot_response.usage.total_tokens

            chatbot_message = chatbot_response.choices[0].message
            mcp_tool_calls = chatbot_message.tool_calls or []


            # Append assistant message
            chatbot_messages.append(
                {
                    "role": "assistant",
                    "content": chatbot_message.content,
                    "tool_calls": mcp_tool_calls,
                },
            )

            if not mcp_tool_calls:
                session_chat.append({"role": "assistant", "content": chatbot_message.content})
                try:
                    await ChatService.update_session_response(session_id, session_chat)
                    logger.info(f"Updated bot response for session {session_id}")
                except Exception as e:
                    logger.error(f"Failed to update bot response: {e}")
                return (
                    chatbot_message.content,
                    chatbot_token_usage,
                    mcp_tools_used,
                    mcp_tools_response,
                )

            # Process each tool call
            for tool_call in mcp_tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_id = tool_call.id

                mcp_tools_used.append(tool_name)

                chatbot_session = self.tool_sessions.get(tool_name)
                if not chatbot_session:
                    error_msg = f"MCP Tool: '{tool_name}' not found"
                    logger.warning(error_msg)
                    chatbot_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": error_msg,
                        },
                    )
                    mcp_tools_response.append(
                        ToolResponse(
                            tool_name=tool_name,
                            args=tool_args,
                            success=False,
                            content="Tool not found",
                        ),
                    )
                    continue

                try:
                    tool_result = await chatbot_session.call_tool(
                        tool_name,
                        arguments=tool_args,
                    )
                    tool_result_content = str(tool_result.content)

                    chatbot_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": tool_result_content,
                        },
                    )
                    mcp_tools_response.append(
                        ToolResponse(
                            tool_name=tool_name,
                            args=tool_args,
                            success=True,
                            content=tool_result_content,
                        ),
                    )

                except Exception as e:
                    error_msg = f"MCP Tool call failed: {e!s}"
                    logger.error(error_msg)
                    chatbot_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": error_msg,
                        },
                    )
                    mcp_tools_response.append(
                        ToolResponse(
                            tool_name=tool_name,
                            args=tool_args,
                            success=False,
                            content="Tool not found",
                        ),
                    )

    async def _register_tools(self, session: ClientSession) -> None:
        """
        Internal method to query all tools from a connected MCP session,
        and save them in available_mcp_tools for OpenAI to use.
        """
        try:
            tools_metadata = await session.list_tools()
            for tool in tools_metadata.tools:
                self.tool_sessions[tool.name] = session
                self.available_mcp_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    },
                )
        except Exception as e:
            logger.warning(f"Failed to list mcp tools: {e}")