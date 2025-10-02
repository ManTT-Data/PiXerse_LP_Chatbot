from mcp.server.fastmcp import FastMCP

from core.db.meta import async_session
from core.db.repositories.blog_repository import BlogRepository
from core.db.repositories.member_repository import MemberRepository
from core.db.repositories.project_repository import ProjectRepository 
from core.db.db_schemas import Blog, Member, Project


def model_to_dict(obj):
    """Convert SQLAlchemy model to dictionary"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # Convert datetime to string for JSON serialization
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        result[column.name] = value
    return result

def tuple_to_dict(row_tuple, column_names):
    """Convert tuple result to dictionary"""
    if row_tuple is None:
        return None
    
    result = {}
    for i, column_name in enumerate(column_names):
        value = row_tuple[i] if i < len(row_tuple) else None
        # Convert datetime to string for JSON serialization
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        result[column_name] = value
    return result

mcp_server = FastMCP("Pixerse-mcp")


# BLOG TOOLS
@mcp_server.tool(
    description="""
    Get detailed information (id, title, content, author, related project, ...) about a specific blog by its ID.
    This tool is used to retrieve more detailed information if the blog ID is already available based on the get_blogs_description tool.
    """,
)
async def get_blog_by_id(blog_id: int):
    async with async_session() as db:
        try:
            blogs = await BlogRepository.get_blog_by_id(
                db, 
                blog_id
            )
            if blogs:
                return {"success": True, "data": model_to_dict(blogs)}
            return {"success": False, "error": "Blog not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="""
    Retrieve a list of all blogs with their id, title, and content.
    This tool can be used to get the id of all blogs, then the get_blog_by_id tool can be used to find more details of one or a few specific blogs.
    """,
)
async def get_blogs_description(limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            blogs = await BlogRepository.get_blogs_description(db, limit, offset)
            column_names = ["blog_id", "title", "content"]
            return {
                "success": True,
                "count": len(blogs),
                "data": [tuple_to_dict(b, column_names) for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search blogs by keyword in blog content. And get detailed information (id, title, content, author, related project, ...) about matched blogs.",
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
                "data": [model_to_dict(b) for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        
# MEMBER TOOLS
@mcp_server.tool(
    description="""
    Get detailed information (id, name, role, summary, project, avatar_url, team_type ...) about a specific member by their ID.
    This tool is used to retrieve more detailed information if the member ID is already available based on the get_members_description tool.
    """,
)
async def get_member_by_id(member_id: int):
    async with async_session() as db:
        try:
            member = await MemberRepository.get_member_by_id(db, member_id)
            if member:
                return {"success": True, "data": model_to_dict(member)}
            return {"success": False, "error": "Member not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="""
    Retrieve a list of all members with their id, name, and summary.
    This tool can be used to get the id of all members, then the get_member_by_id tool can be used to find more details of one or a few specific members.
    """,
)
async def get_members_description(limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            members = await MemberRepository.get_members_description(db, limit, offset)
            column_names = ["member_id", "member_name", "role", "summary"]
            return {
                "success": True,
                "count": len(members),
                "data": [tuple_to_dict(m, column_names) for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search members by keyword in their summary. And get detailed information (id, name, role, summary, project, avatar_url, ...) about matched members.",
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
                "data": [model_to_dict(m) for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# PROJECT TOOLS
@mcp_server.tool(
    description="""
    Get detailed information (id, name, description, ...) about a specific project by its ID.
    This tool is used to retrieve more detailed information if the project ID is already available based on the get_projects_description tool.
    """,
)
async def get_project_by_id(project_id: int):
    async with async_session() as db:
        try:
            project = await ProjectRepository.get_project_by_id(db, project_id)
            if project:
                return {"success": True, "data": model_to_dict(project)}
            return {"success": False, "error": "Project not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="""
    Retrieve a list of all projects with their id, name, and description.
    This tool can be used to get the id of all projects, then the get_project_by_id tool can be used to find more details of one or a few specific projects.
    """,
)
async def get_projects_description(limit: int = 50, offset: int = 0):
    async with async_session() as db:
        try:
            projects = await ProjectRepository.get_projects_description(db, limit, offset)
            column_names = ["project_id", "project_name", "description"]
            return {
                "success": True,
                "count": len(projects),
                "data": [tuple_to_dict(p, column_names) for p in projects],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search projects by keyword in their description. And get detailed information (id, name, description, ...) about matched projects.",
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
                "data": [model_to_dict(p) for p in projects],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp_server.run(transport="stdio")
