#!/usr/bin/env python3
"""
MCP Server for PiXerse Team chatbot
Exposes tools via Model Context Protocol for LLM clients to use
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from core.services.mcp_tools import get_mcp_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pixerse-mcp-server")

# Initialize MCP server
server = Server("pixerse-team-chatbot")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available MCP tools"""
    return [
        # Projects tools
        types.Tool(
            name="projects_description",
            description="Get all project names and descriptions for semantic matching",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="projects_get",
            description="Get detailed information about a specific project by ID, with optional related data",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer"},
                    "with_members": {"type": "boolean", "default": True},
                    "with_blogs": {"type": "boolean", "default": True},
                    "with_assets": {"type": "boolean", "default": True}
                },
                "required": ["project_id"]
            }
        ),
        types.Tool(
            name="projects_list",
            description="List projects with search, sorting, and pagination support",
            inputSchema={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "Search keyword for project name/description"},
                    "order_by": {"type": "string", "enum": ["created_at", "updated_at", "project_name"], "default": "updated_at"},
                    "order_dir": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
                    "limit": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100},
                    "offset": {"type": "integer", "default": 0}
                }
            }
        ),
        
        # Members tools
        types.Tool(
            name="members_description",
            description="Get all member names, roles and summaries for semantic matching",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="members_get",
            description="Get detailed information about a specific member by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "member_id": {"type": "integer"},
                    "with_project": {"type": "boolean", "default": True},
                    "with_assets": {"type": "boolean", "default": False}
                },
                "required": ["member_id"]
            }
        ),
        types.Tool(
            name="members_search",
            description="Search and filter members by role, team type, keywords, or project",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "Filter by member role"},
                    "team_type": {"type": "string", "description": "Filter by team type"},
                    "q": {"type": "string", "description": "Search in name/summary"},
                    "project_id": {"type": "integer", "description": "Filter by project ID"},
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0}
                }
            }
        ),
        
        # Blogs tools
        types.Tool(
            name="blogs_description",
            description="Get all blog titles and content previews for semantic matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 100}
                }
            }
        ),
        types.Tool(
            name="blogs_get",
            description="Get detailed information about a specific blog post by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "blog_id": {"type": "integer"},
                    "with_author": {"type": "boolean", "default": True},
                    "with_assets": {"type": "boolean", "default": True}
                },
                "required": ["blog_id"]
            }
        ),
        types.Tool(
            name="blogs_list",
            description="List blog posts with filtering, search, and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "Filter by project"},
                    "category": {"type": "string", "enum": ["tutorial", "news", "showcase"], "description": "Filter by category"},
                    "tag": {"type": "string", "description": "Filter by tag"},
                    "q": {"type": "string", "description": "Search in title/content"},
                    "order_by": {"type": "string", "enum": ["created_at", "updated_at"], "default": "created_at"},
                    "order_dir": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0}
                }
            }
        ),
        
        # Assets tools
        types.Tool(
            name="assets_description",
            description="Get all asset filenames, types and descriptions for semantic matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 100}
                }
            }
        ),
        types.Tool(
            name="assets_get",
            description="Get detailed information about a specific asset and its usage",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "integer"}
                },
                "required": ["asset_id"]
            }
        ),
        types.Tool(
            name="assets_search",
            description="Search assets with filters for type, filename, associations",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_type": {"type": "string", "enum": ["IMAGE", "VIDEO", "YOUTUBE"]},
                    "q": {"type": "string", "description": "Search filename/description"},
                    "mime_type": {"type": "string"},
                    "project_id": {"type": "integer"},
                    "blog_id": {"type": "integer"},
                    "member_id": {"type": "integer"},
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0}
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls from MCP clients"""
    try:
        # Get MCP tools instance
        tools = get_mcp_tools()
        
        # Route to appropriate tool method
        if name == "projects_description":
            result = tools.projects_description()
        elif name == "projects_get":
            result = tools.projects_get(**arguments)
        elif name == "projects_list":
            result = tools.projects_list(**arguments)
        elif name == "members_description":
            result = tools.members_description()
        elif name == "members_get":
            result = tools.members_get(**arguments)
        elif name == "members_search":
            result = tools.members_search(**arguments)
        elif name == "blogs_description":
            result = tools.blogs_description(**arguments)
        elif name == "blogs_get":
            result = tools.blogs_get(**arguments)
        elif name == "blogs_list":
            result = tools.blogs_list(**arguments)
        elif name == "assets_description":
            result = tools.assets_description(**arguments)
        elif name == "assets_get":
            result = tools.assets_get(**arguments)
        elif name == "assets_search":
            result = tools.assets_search(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Return result as TextContent
        return [
            types.TextContent(
                type="text", 
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]
        
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": str(e)}, ensure_ascii=False)
            )
        ]
    finally:
        # Close database session
        try:
            tools.db.close()
        except:
            pass


async def main():
    """Main entry point for MCP server"""
    # Initialize server options
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pixerse-team-chatbot",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())