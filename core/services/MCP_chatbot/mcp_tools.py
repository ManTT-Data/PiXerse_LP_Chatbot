from mcp.server.fastmcp import FastMCP
from datetime import datetime

from core.db.meta import async_session
from core.db.repositories.strapi_blog_repository import StrapiBlogRepository
from core.db.repositories.strapi_member_repository import StrapiMemberRepository
from core.db.repositories.strapi_project_repository import StrapiProjectRepository
from core.db.strapi_schemas import Blog, Member, Project


def model_to_dict(obj):
    """Convert SQLAlchemy model to dictionary"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # Convert datetime to string for JSON serialization
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result

mcp_server = FastMCP("Pixerse-mcp")


# BLOG TOOLS
@mcp_server.tool(
    description="Get detailed information about a specific blog by its ID, including user, project, tags, categories, and authors.",
)
async def get_blog_by_id(blog_id: int):
    """Get blog by ID with all relations"""
    async with async_session() as db:
        try:
            blog = await StrapiBlogRepository.get_blog_by_id(db, blog_id, include_relations=True)
            if blog:
                blog_dict = model_to_dict(blog)
                # Add related data
                if blog.project:
                    blog_dict['project'] = [{'id': blog.project.id, 'name': blog.project.name}] if isinstance(blog.project, list) and blog.project else ({'id': blog.project.id, 'name': blog.project.name} if hasattr(blog.project, 'id') else None)
                if blog.tags:
                    blog_dict['tags'] = [{'id': t.id, 'name': t.name} for t in blog.tags]
                if blog.categories:
                    blog_dict['categories'] = [{'id': c.id, 'name': c.name} for c in blog.categories]
                if blog.authors:
                    blog_dict['authors'] = [{'id': a.id, 'name': a.name} for a in blog.authors]
                
                return {"success": True, "data": blog_dict}
            return {"success": False, "error": "Blog not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Retrieve a list of blogs with their id, title, and content summary. Supports pagination.",
)
async def get_blogs_description(limit: int = 50, offset: int = 0, published_only: bool = False):
    """Get list of blogs with pagination"""
    async with async_session() as db:
        try:
            blogs = await StrapiBlogRepository.get_all_blogs(db, limit, offset, published_only)
            return {
                "success": True,
                "count": len(blogs),
                "data": [model_to_dict(b) for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search blogs by keyword in title or content. Returns matching blogs.",
)
async def get_blogs_by_keyword(keyword: str, limit: int = 50, offset: int = 0):
    """Search blogs by keyword"""
    async with async_session() as db:
        try:
            blogs = await StrapiBlogRepository.search_blogs_by_keyword(db, keyword, limit, offset)
            return {
                "success": True,
                "count": len(blogs),
                "keyword": keyword,
                "data": [model_to_dict(b) for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Get all blogs associated with a specific project by project ID.",
)
async def get_blogs_by_project(project_id: int, limit: int = 50):
    """Get blogs by project"""
    async with async_session() as db:
        try:
            blogs = await StrapiBlogRepository.get_blogs_by_project(db, project_id, limit)
            return {
                "success": True,
                "project_id": project_id,
                "count": len(blogs),
                "data": [model_to_dict(b) for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        
# MEMBER TOOLS
@mcp_server.tool(
    description="Get detailed information about a specific team member by their ID, including associated projects.",
)
async def get_member_by_id(member_id: int):
    """Get member by ID with projects"""
    async with async_session() as db:
        try:
            member = await StrapiMemberRepository.get_member_by_id(db, member_id, include_projects=True)
            if member:
                member_dict = model_to_dict(member)
                # Add projects
                if member.projects:
                    member_dict['projects'] = [
                        {'id': p.id, 'name': p.name, 'description': p.description} 
                        for p in member.projects
                    ]
                return {"success": True, "data": member_dict}
            return {"success": False, "error": "Member not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Retrieve a list of all team members with their id, name, role, and summary. Supports pagination.",
)
async def get_members_description(limit: int = 50, offset: int = 0, published_only: bool = False):
    """Get list of members with pagination"""
    async with async_session() as db:
        try:
            members = await StrapiMemberRepository.get_all_members(db, limit, offset, published_only)
            return {
                "success": True,
                "count": len(members),
                "data": [model_to_dict(m) for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search team members by keyword in name, summary, or role. Useful for finding members with specific skills or expertise.",
)
async def get_members_by_skill_keyword(keyword: str, limit: int = 50, offset: int = 0):
    """Search members by keyword"""
    async with async_session() as db:
        try:
            members = await StrapiMemberRepository.search_members_by_keyword(db, keyword, limit, offset)
            return {
                "success": True,
                "count": len(members),
                "keyword": keyword,
                "data": [model_to_dict(m) for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Get all members of a specific team type (e.g., 'Development', 'Design', 'Marketing').",
)
async def get_members_by_team_type(team_type: str, limit: int = 50):
    """Get members by team type"""
    async with async_session() as db:
        try:
            members = await StrapiMemberRepository.get_members_by_team_type(db, team_type, limit)
            return {
                "success": True,
                "team_type": team_type,
                "count": len(members),
                "data": [model_to_dict(m) for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# PROJECT TOOLS
@mcp_server.tool(
    description="Get detailed information about a specific project by its ID, including technologies, members, and blogs.",
)
async def get_project_by_id(project_id: int):
    """Get project by ID with all relations"""
    async with async_session() as db:
        try:
            project = await StrapiProjectRepository.get_project_by_id(db, project_id, include_relations=True)
            if project:
                project_dict = model_to_dict(project)
                # Add related data
                if project.technologies:
                    project_dict['technologies'] = [
                        {'id': t.id, 'name': t.name} 
                        for t in project.technologies
                    ]
                if project.members:
                    project_dict['members'] = [
                        {'id': m.id, 'name': m.name, 'role': m.role} 
                        for m in project.members
                    ]
                return {"success": True, "data": project_dict}
            return {"success": False, "error": "Project not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Retrieve a list of all projects with their id, name, and description. Supports pagination.",
)
async def get_projects_description(limit: int = 50, offset: int = 0, published_only: bool = False):
    """Get list of projects with pagination"""
    async with async_session() as db:
        try:
            projects = await StrapiProjectRepository.get_all_projects(db, limit, offset, published_only)
            return {
                "success": True,
                "count": len(projects),
                "data": [model_to_dict(p) for p in projects],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Search projects by keyword in name or description. Returns matching projects.",
)
async def get_projects_by_keywords(keyword: str, limit: int = 50, offset: int = 0):
    """Search projects by keyword"""
    async with async_session() as db:
        try:
            projects = await StrapiProjectRepository.search_projects_by_keyword(db, keyword, limit, offset)
            return {
                "success": True,
                "count": len(projects),
                "keyword": keyword,
                "data": [model_to_dict(p) for p in projects],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="Get all projects that use a specific technology by technology ID.",
)
async def get_projects_by_technology(technology_id: int, limit: int = 50):
    """Get projects by technology"""
    async with async_session() as db:
        try:
            projects = await StrapiProjectRepository.get_projects_by_technology(db, technology_id, limit)
            return {
                "success": True,
                "technology_id": technology_id,
                "count": len(projects),
                "data": [model_to_dict(p) for p in projects],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp_server.run(transport="stdio")
