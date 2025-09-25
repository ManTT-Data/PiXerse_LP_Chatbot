from distutils import core
from mcp.server.fastmcp import FastMCP

from core.db.meta import async_session
from core.db.repositories.blog_repository import BlogRepository
from core.db.repositories.member_repository import MemberRepository
from core.db.repositories.project_repository import ProjectRepository 
from core.db.db_schemas import Blog, Member, Project

mcp_server = FastMCP("Pixerse-mcp")


# BLOG TOOLS
@mcp_server.tool(
    description="Get detailed information about a specific blog by its ID.",
)
async def get_blog_by_id(blog_id: int):
    async with async_session() as db:
        try:
            blogs = await BlogRepository.get_blog_by_id(
                db, 
                blog_id
            )
            if blogs:
                return {"success": True, "count": len(blogs), "data": blogs.model_dump()}
            return {"success": False, "error": "Blog not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Retrieve a list of blogs with their id, title, and content.",
)
async def get_blogs_description(limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            blogs = await BlogRepository.get_blogs_description(db, limit, offset)
            return {
                "success": True,
                "count": len(blogs),
                "data": [b.model_dump() for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search blogs by keyword in blog content.",
)
async def get_blogs_by_keyword(keyword: str, limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            blogs = await BlogRepository.get_blogs_by_keywords(
                db,
                keyword,
                limit,
                offset,
            )
            return {
                "success": True,
                "count": len(blogs),
                "data": [b.model_dump() for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        
# MEMBER TOOLS
@mcp_server.tool(
    description="Get detailed information about a specific member by their ID.",
)
async def get_member_by_id(member_id: int):
    async with async_session() as db:
        try:
            member = await MemberRepository.get_member_by_id(db, member_id)
            if member:
                return {"success": True, "data": member.model_dump()}
            return {"success": False, "error": "Member not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Retrieve a list of members with their id, name, and summary.",
)
async def get_members_description(limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            members = await MemberRepository.get_members_description(db, limit, offset)
            return {
                "success": True,
                "count": len(members),
                "data": [m.model_dump() for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search members by keyword in their summary.",
)
async def get_members_by_skill_keyword(keyword: str, limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            members = await MemberRepository.get_members_by_skill_keyword(
                db,
                keyword,
                limit,
                offset,
            )
            return {
                "success": True,
                "count": len(members),
                "data": [m.model_dump() for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# PROJECT TOOLS
@mcp_server.tool(
    description="Get detailed information about a specific project by its ID.",
)
async def get_project_by_id(project_id: int):
    async with async_session() as db:
        try:
            project = await ProjectRepository.get_project_by_id(db, project_id)
            if project:
                return {"success": True, "data": project.model_dump()}
            return {"success": False, "error": "Project not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Retrieve a list of projects with their id, name, and description.",
)
async def get_projects_description(limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            projects = await ProjectRepository.get_projects_description(db, limit, offset)
            return {
                "success": True,
                "count": len(projects),
                "data": [p.model_dump() for p in projects],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search projects by keyword in their description.",
)
async def get_projects_by_keywords(keyword: str, limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            projects = await ProjectRepository.get_projects_by_keywords(
                db,
                keyword,
                limit,
                offset,
            )
            return {
                "success": True,
                "count": len(projects),
                "data": [p.model_dump() for p in projects],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp_server.run(transport="stdio")
