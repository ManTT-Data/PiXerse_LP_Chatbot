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
from core.settings.base import settings


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
    ) -> Tuple[str, int, List[str], List[Dict[str, Any]]]:
        """
        Main method to handle a user query:
        - Sends the message to OpenAI Chat API
        - If tools are required, calls them via MCP
        - Collects tool responses and returns final output
        """
        chatbot_messages = [
            {
                "role": "system",
                "content": (SYSTEM_PROMPT),
            },
            {"role": "user", "content": query},
        ]
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

            if not mcp_tool_calls:
                return (
                    chatbot_message.content,
                    chatbot_token_usage,
                    mcp_tools_used,
                    mcp_tools_response,
                )

            # Append assistant message
            chatbot_messages.append(
                {
                    "role": "assistant",
                    "content": chatbot_message.content,
                    "tool_calls": mcp_tool_calls,
                },
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