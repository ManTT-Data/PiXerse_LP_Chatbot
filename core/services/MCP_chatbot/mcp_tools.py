from mcp.server.fastmcp import FastMCP
from datetime import datetime

from core.db.meta import async_session
from core.db.repositories.blog_repository import StrapiBlogRepository
from core.db.repositories.member_repository import StrapiMemberRepository
from core.db.repositories.project_repository import StrapiProjectRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Row, RowMapping
from typing import Any
from dataclasses import is_dataclass, asdict
from collections.abc import Mapping



def model_to_dict(obj: Any):
    """Convert ORM / Row / Mapping / tuple / dataclass → dict (JSON-ready)."""
    if obj is None:
        return None

    # 1) ORM instance (có __table__)
    if hasattr(obj, "__table__"):
        out = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            out[col.name] = val.isoformat() if isinstance(val, datetime) else val
        return out

    # 2) SQLAlchemy Row/RowMapping (mọi phiên bản) — ưu tiên dùng _mapping nếu có
    if hasattr(obj, "_mapping"):
        d = dict(obj._mapping)
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        return d

    # 3) Mapping python (dict, RowMapping implement Mapping)
    if isinstance(obj, Mapping):
        return {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in obj.items()}

    # 4) Dataclass
    if is_dataclass(obj):
        d = asdict(obj)
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        return d

    # 5) Tuple/List → cố gắng đoán dạng (k, v) hoặc đánh số col
    if isinstance(obj, (tuple, list)):
        try:
            if all(isinstance(x, (tuple, list)) and len(x) == 2 for x in obj):
                return {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in obj}
        except Exception:
            pass
        return {f"col{i}": (v.isoformat() if isinstance(v, datetime) else v) for i, v in enumerate(obj)}

    # 6) Primitive → bọc lại
    return {"value": obj}

mcp_server = FastMCP("Pixerse-mcp")


# BLOG TOOLS
@mcp_server.tool(
    description="""
    Get detailed information (id, title, content, author, related project, ...)
      about a specific blog by its ID. This tool is used to retrieve more detailed 
      information if the blog ID is already available based on the list_blogs_description tool.
    """
)
async def get_blog_by_id(blog_id: int):
    """Get blog by ID with all relations"""
    async with async_session() as db:
        try:
            blog = await StrapiBlogRepository.get_blog_by_id(db, blog_id)
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
    description="""
    Retrieve a list of all blogs with their id, title, and content. This tool can 
    be used to get the id of all blogs, then the get_blog_by_id tool can be used to 
    find more details of one or a few specific blogs.
    """,
)
async def list_blogs_content(limit: int = 50):
    """Get list of blogs with pagination"""
    async with async_session() as db:
        try:
            blogs = await StrapiBlogRepository.get_all_blogs_content(db, limit)
            return {
                "success": True,
                "count": len(blogs),
                "data": [model_to_dict(b) for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="""
    Search blogs by keyword in blog content. And get detailed information (id, 
    title, content, author, related project, ...) about matched blogs.
    """
)
async def get_blogs_by_keyword(keyword: str, limit: int = 50):
    """Search blogs by keyword"""
    async with async_session() as db:
        try:
            blogs = await StrapiBlogRepository.search_blogs_by_keyword(db, keyword, limit)
            return {
                "success": True,
                "count": len(blogs),
                "keyword": keyword,
                "data": [model_to_dict(b) for b in blogs],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

        
# MEMBER TOOLS
@mcp_server.tool(
    description="""
    Get detailed information (id, name, role, summary, project, avatar_url, 
    team_type ...) about a specific member by their ID. This tool is used to 
    retrieve more detailed information if the member ID is already available 
    based on the list_members_description tool.
    """
)
async def get_member_by_id(member_id: int):
    """Get member by ID with projects"""
    async with async_session() as db:
        try:
            member = await StrapiMemberRepository.get_member_by_id(db, member_id)
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
    description="""
    Retrieve a list of all members with their id, name, and summary. 
    This tool can be used to get the id of all members, then the get_member_by_id 
    tool can be used to find more details of one or a few specific members.
    """
)
async def list_members_summary(limit: int = 50):
    """Get list of members with pagination"""
    async with async_session() as db:
        try:
            members = await StrapiMemberRepository.get_all_members_summary(db, limit)
            return {
                "success": True,
                "count": len(members),
                "data": [model_to_dict(m) for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


@mcp_server.tool(
    description="""
    Search members by keyword in their summary. And get detailed information (id, 
    name, role, summary, project, avatar_url, ...) about matched members.    
    """
)
async def get_members_by_keyword(keyword: str, limit: int = 50):
    """Search members by keyword"""
    async with async_session() as db:
        try:
            members = await StrapiMemberRepository.search_members_by_keyword(db, keyword, limit)
            return {
                "success": True,
                "count": len(members),
                "keyword": keyword,
                "data": [model_to_dict(m) for m in members],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# PROJECT TOOLS
@mcp_server.tool(
    description="""
    Get detailed information (id, name, description, contributor, url, ...) 
    about a specific project by their ID. This tool is used to retrieve more detailed 
    information if the project ID is already available based on the list_projects_description tool.
    """
)
async def get_project_by_id(project_id: int):
    """Get project by ID with all relations"""
    async with async_session() as db:
        try:
            project = await StrapiProjectRepository.get_project_by_id(db, project_id)
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
    description="""
    Retrieve a list of all projects with their id, name, and description. 
    This tool can be used to get the id of all projects, then the get_project_by_id 
    tool can be used to find more details of one or a few specific projects.
    """
)
async def list_projects_description(limit: int = 50):
    """Get list of projects with pagination"""
    async with async_session() as db:
        try:
            projects = await StrapiProjectRepository.get_all_projects_description(db, limit)
            return {
                "success": True,
                "count": len(projects),
                "data": [model_to_dict(p) for p in projects],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        

if __name__ == "__main__":
    mcp_server.run(transport="stdio")
