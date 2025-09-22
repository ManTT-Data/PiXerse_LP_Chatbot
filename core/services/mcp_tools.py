from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.db.database import get_db_session
from core.schemas.models import Project, Member, Blog, Asset, BlogAsset
import json


class MCPTools:
    """MCP Tools for PiXerse Team chatbot"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    # ==================== PROJECTS TOOLS ====================
    
    def projects_description(self) -> List[Dict[str, Any]]:
        """
        Return the project_id, project_name, and project_description of all projects in the database.
        Example use cases:
        - User asks for "a project related to web3" → tool gives all names/descriptions → model infers which one fits.
        - User asks about projects in general → tool can summarize all projects.
        """
        query = text("""
            SELECT project_id, project_name, project_description
            FROM projects
            ORDER BY updated_at DESC;
        """)
        
        result = self.db.execute(query)
        projects = []
        for row in result:
            projects.append({
                "project_id": row.project_id,
                "project_name": row.project_name,
                "project_description": row.project_description
            })
        return projects

    def projects_get(self, project_id: int, with_members: bool = True, 
                    with_blogs: bool = True, with_assets: bool = True) -> Dict[str, Any]:
        """
        Fetch detailed information about a single project by its ID.
        This tool can optionally include related members, blog posts, and assets linked to the project.
        """
        # Get project basic info
        project_query = text("SELECT * FROM projects WHERE project_id = :project_id")
        project_result = self.db.execute(project_query, {"project_id": project_id}).first()
        
        if not project_result:
            return {"error": "Project not found"}
        
        project_data = {
            "project_id": project_result.project_id,
            "project_name": project_result.project_name,
            "project_description": project_result.project_description,
            "created_at": project_result.created_at.isoformat() if project_result.created_at else None,
            "updated_at": project_result.updated_at.isoformat() if project_result.updated_at else None
        }
        
        # Get members if requested
        if with_members:
            members_query = text("SELECT * FROM members WHERE project_id = :project_id")
            members_result = self.db.execute(members_query, {"project_id": project_id})
            project_data["members"] = []
            for member in members_result:
                project_data["members"].append({
                    "member_id": member.member_id,
                    "member_name": member.member_name,
                    "member_role": member.member_role,
                    "team_type": member.team_type,
                    "summary": member.summary
                })
        
        # Get blogs if requested
        if with_blogs:
            blogs_query = text("SELECT * FROM blogs WHERE project_id = :project_id ORDER BY created_at DESC")
            blogs_result = self.db.execute(blogs_query, {"project_id": project_id})
            project_data["blogs"] = []
            for blog in blogs_result:
                project_data["blogs"].append({
                    "blog_id": blog.blog_id,
                    "blog_title": blog.blog_title,
                    "category": blog.category,
                    "tags": blog.tags,
                    "created_at": blog.created_at.isoformat() if blog.created_at else None
                })
        
        # Get assets associated with blogs of this project
        if with_assets:
            assets_query = text("""
                SELECT DISTINCT a.* FROM assets a
                JOIN blog_assets ba ON ba.asset_id = a.asset_id
                JOIN blogs b ON b.blog_id = ba.blog_id
                WHERE b.project_id = :project_id
                ORDER BY a.created_at DESC
            """)
            try:
                assets_result = self.db.execute(assets_query, {"project_id": project_id})
                project_data["assets"] = []
                for asset in assets_result:
                    project_data["assets"].append({
                        "asset_id": asset.asset_id,
                        "filename": asset.filename,
                        "asset_type": asset.asset_type,
                        "description": asset.description
                    })
            except:
                # If blog_assets relationship doesn't exist, skip assets
                project_data["assets"] = []
        
        return project_data

    def projects_list(self, q: Optional[str] = None, order_by: str = "updated_at", 
                     order_dir: str = "desc", limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Deep search of projects in database based on keywords
        """
        # Build the WHERE clause
        where_clause = ""
        params = {"limit": limit, "offset": offset}
        
        if q:
            where_clause = """
                WHERE (project_name LIKE CONCAT('%', :q, '%')
                   OR project_description LIKE CONCAT('%', :q, '%'))
            """
            params["q"] = q
        
        # Build ORDER BY clause
        valid_order_fields = ["created_at", "updated_at", "project_name"]
        if order_by not in valid_order_fields:
            order_by = "updated_at"
        
        if order_dir.lower() not in ["asc", "desc"]:
            order_dir = "desc"
        
        query = text(f"""
            SELECT * FROM projects
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT :limit OFFSET :offset
        """)
        
        result = self.db.execute(query, params)
        projects = []
        for row in result:
            projects.append({
                "project_id": row.project_id,
                "project_name": row.project_name,
                "project_description": row.project_description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None
            })
        
        return projects

    # ==================== MEMBERS TOOLS ====================
    
    def members_description(self) -> List[Dict[str, Any]]:
        """
        Return the member_id, member_name, and summary (or member_role) of all members.
        This tool allows the model to scan through all member summaries to answer semantic questions.
        """
        query = text("""
            SELECT member_id, member_name, member_role, summary
            FROM members
            ORDER BY updated_at DESC
        """)
        
        result = self.db.execute(query)
        members = []
        for row in result:
            members.append({
                "member_id": row.member_id,
                "member_name": row.member_name,
                "member_role": row.member_role,
                "summary": row.summary
            })
        return members

    def members_get(self, member_id: int, with_project: bool = True, 
                   with_assets: bool = False) -> Dict[str, Any]:
        """
        Retrieve a single member's profile by their ID.
        """
        # Get member basic info
        member_query = text("SELECT * FROM members WHERE member_id = :member_id")
        member_result = self.db.execute(member_query, {"member_id": member_id}).first()
        
        if not member_result:
            return {"error": "Member not found"}
        
        member_data = {
            "member_id": member_result.member_id,
            "member_name": member_result.member_name,
            "member_role": member_result.member_role,
            "team_type": member_result.team_type,
            "summary": member_result.summary,
            "avatar_url": member_result.avatar_url,
            "project_id": member_result.project_id,
            "created_at": member_result.created_at.isoformat() if member_result.created_at else None,
            "updated_at": member_result.updated_at.isoformat() if member_result.updated_at else None
        }
        
        # Get project info if requested
        if with_project and member_result.project_id:
            project_query = text("""
                SELECT p.* FROM projects p
                JOIN members m ON m.project_id = p.project_id
                WHERE m.member_id = :member_id
            """)
            project_result = self.db.execute(project_query, {"member_id": member_id}).first()
            if project_result:
                member_data["project"] = {
                    "project_id": project_result.project_id,
                    "project_name": project_result.project_name,
                    "project_description": project_result.project_description
                }
        
        # Get assets if requested (assuming member_assets table exists)
        if with_assets:
            assets_query = text("""
                SELECT a.* FROM assets a
                JOIN member_assets ma ON ma.asset_id = a.asset_id
                WHERE ma.member_id = :member_id
                ORDER BY a.created_at DESC
            """)
            try:
                assets_result = self.db.execute(assets_query, {"member_id": member_id})
                member_data["assets"] = []
                for asset in assets_result:
                    member_data["assets"].append({
                        "asset_id": asset.asset_id,
                        "filename": asset.filename,
                        "asset_type": asset.asset_type,
                        "description": asset.description
                    })
            except:
                member_data["assets"] = []
        
        return member_data

    def members_search(self, role: Optional[str] = None, team_type: Optional[str] = None,
                      q: Optional[str] = None, project_id: Optional[int] = None,
                      limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Deep search of members in database based on keywords
        """
        where_conditions = []
        params = {"limit": limit, "offset": offset}
        
        if role:
            where_conditions.append("member_role LIKE CONCAT('%', :role, '%')")
            params["role"] = role
            
        if team_type:
            where_conditions.append("team_type LIKE CONCAT('%', :team_type, '%')")
            params["team_type"] = team_type
            
        if q:
            where_conditions.append("(member_name LIKE CONCAT('%', :q, '%') OR summary LIKE CONCAT('%', :q, '%'))")
            params["q"] = q
            
        if project_id:
            where_conditions.append("project_id = :project_id")
            params["project_id"] = project_id
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        query = text(f"""
            SELECT * FROM members
            {where_clause}
            ORDER BY updated_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = self.db.execute(query, params)
        members = []
        for row in result:
            members.append({
                "member_id": row.member_id,
                "member_name": row.member_name,
                "member_role": row.member_role,
                "team_type": row.team_type,
                "summary": row.summary,
                "avatar_url": row.avatar_url,
                "project_id": row.project_id,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None
            })
        
        return members

    # ==================== BLOGS TOOLS ====================
    
    def blogs_description(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Return the blog_id, blog_title, and blog_content (shortened/first N chars) of all blog posts.
        """
        query = text("""
            SELECT blog_id, blog_title, LEFT(blog_content, 500) AS preview
            FROM blogs
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        
        result = self.db.execute(query, {"limit": limit})
        blogs = []
        for row in result:
            blogs.append({
                "blog_id": row.blog_id,
                "blog_title": row.blog_title,
                "preview": row.preview
            })
        return blogs

    def blogs_get(self, blog_id: int, with_author: bool = True, 
                 with_assets: bool = True) -> Dict[str, Any]:
        """
        Retrieve detailed information about a single blog post by its ID.
        """
        # Get blog basic info
        blog_query = text("SELECT * FROM blogs WHERE blog_id = :blog_id")
        blog_result = self.db.execute(blog_query, {"blog_id": blog_id}).first()
        
        if not blog_result:
            return {"error": "Blog not found"}
        
        blog_data = {
            "blog_id": blog_result.blog_id,
            "project_id": blog_result.project_id,
            "blog_title": blog_result.blog_title,
            "blog_content": blog_result.blog_content,
            "author_id": blog_result.author_id,
            "category": blog_result.category,
            "tags": blog_result.tags,
            "featured_image": blog_result.featured_image,
            "created_at": blog_result.created_at.isoformat() if blog_result.created_at else None,
            "updated_at": blog_result.updated_at.isoformat() if blog_result.updated_at else None
        }
        
        # Get author info if requested
        if with_author:
            author_query = text("""
                SELECT m.* FROM members m 
                JOIN blogs b ON b.author_id = m.member_id 
                WHERE b.blog_id = :blog_id
            """)
            author_result = self.db.execute(author_query, {"blog_id": blog_id}).first()
            if author_result:
                blog_data["author"] = {
                    "member_id": author_result.member_id,
                    "member_name": author_result.member_name,
                    "member_role": author_result.member_role,
                    "team_type": author_result.team_type
                }
        
        # Get assets if requested
        if with_assets:
            assets_query = text("""
                SELECT a.* FROM assets a 
                JOIN blog_assets ba ON ba.asset_id = a.asset_id 
                WHERE ba.blog_id = :blog_id
            """)
            assets_result = self.db.execute(assets_query, {"blog_id": blog_id})
            blog_data["assets"] = []
            for asset in assets_result:
                blog_data["assets"].append({
                    "asset_id": asset.asset_id,
                    "filename": asset.filename,
                    "asset_type": asset.asset_type,
                    "cloudinary_url": asset.cloudinary_url,
                    "description": asset.description
                })
        
        return blog_data

    def blogs_list(self, project_id: Optional[int] = None, category: Optional[str] = None,
                  tag: Optional[str] = None, q: Optional[str] = None, 
                  order_by: str = "created_at", order_dir: str = "desc",
                  limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Deep search of blogs in database based on keywords
        """
        where_conditions = []
        params = {"limit": limit, "offset": offset}
        
        if project_id:
            where_conditions.append("project_id = :project_id")
            params["project_id"] = project_id
            
        if category:
            where_conditions.append("category = :category")
            params["category"] = category
            
        if tag:
            # For PostgreSQL JSON search
            where_conditions.append("tags::text LIKE CONCAT('%', :tag, '%')")
            params["tag"] = tag
            
        if q:
            where_conditions.append("(blog_title LIKE CONCAT('%', :q, '%') OR blog_content LIKE CONCAT('%', :q, '%'))")
            params["q"] = q
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Validate order_by
        valid_order_fields = ["created_at", "updated_at"]
        if order_by not in valid_order_fields:
            order_by = "created_at"
            
        if order_dir.lower() not in ["asc", "desc"]:
            order_dir = "desc"
        
        query = text(f"""
            SELECT * FROM blogs
            {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT :limit OFFSET :offset
        """)
        
        result = self.db.execute(query, params)
        blogs = []
        for row in result:
            blogs.append({
                "blog_id": row.blog_id,
                "project_id": row.project_id,
                "blog_title": row.blog_title,
                "author_id": row.author_id,
                "category": row.category,
                "tags": row.tags,
                "featured_image": row.featured_image,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None
            })
        
        return blogs

    # ==================== ASSETS TOOLS ====================
    
    def assets_description(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Return the asset_id, filename, asset_type, and description of all assets.
        """
        query = text("""
            SELECT asset_id, filename, asset_type, description
            FROM assets
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        
        result = self.db.execute(query, {"limit": limit})
        assets = []
        for row in result:
            assets.append({
                "asset_id": row.asset_id,
                "filename": row.filename,
                "asset_type": row.asset_type,
                "description": row.description
            })
        return assets

    def assets_get(self, asset_id: int) -> Dict[str, Any]:
        """
        Fetch metadata and details about a single asset by its ID.
        Also returns all the entities (projects, blogs, members) that this asset is attached to.
        """
        # Get asset basic info
        asset_query = text("SELECT * FROM assets WHERE asset_id = :asset_id")
        asset_result = self.db.execute(asset_query, {"asset_id": asset_id}).first()
        
        if not asset_result:
            return {"error": "Asset not found"}
        
        asset_data = {
            "asset_id": asset_result.asset_id,
            "filename": asset_result.filename,
            "original_filename": asset_result.original_filename,
            "cloudinary_public_id": asset_result.cloudinary_public_id,
            "cloudinary_url": asset_result.cloudinary_url,
            "asset_type": asset_result.asset_type,
            "file_size": asset_result.file_size,
            "mime_type": asset_result.mime_type,
            "youtube_video_id": asset_result.youtube_video_id,
            "description": asset_result.description,
            "created_at": asset_result.created_at.isoformat() if asset_result.created_at else None,
            "updated_at": asset_result.updated_at.isoformat() if asset_result.updated_at else None,
            "attached_to": {
                "projects": [],
                "blogs": [],
                "members": []
            }
        }
        
        # Get attached projects through blog_assets relationship
        try:
            projects_query = text("""
                SELECT DISTINCT p.* FROM projects p
                JOIN blogs b ON b.project_id = p.project_id
                JOIN blog_assets ba ON ba.blog_id = b.blog_id
                WHERE ba.asset_id = :asset_id
            """)
            projects_result = self.db.execute(projects_query, {"asset_id": asset_id})
            for project in projects_result:
                asset_data["attached_to"]["projects"].append({
                    "project_id": project.project_id,
                    "project_name": project.project_name
                })
        except:
            pass
        
        # Get attached blogs
        try:
            blogs_query = text("""
                SELECT b.* FROM blogs b
                JOIN blog_assets ba ON ba.blog_id = b.blog_id
                WHERE ba.asset_id = :asset_id
            """)
            blogs_result = self.db.execute(blogs_query, {"asset_id": asset_id})
            for blog in blogs_result:
                asset_data["attached_to"]["blogs"].append({
                    "blog_id": blog.blog_id,
                    "blog_title": blog.blog_title
                })
        except:
            pass
        
        # Get attached members (if member_assets table exists)
        try:
            members_query = text("""
                SELECT m.* FROM members m
                JOIN member_assets ma ON ma.member_id = m.member_id
                WHERE ma.asset_id = :asset_id
            """)
            members_result = self.db.execute(members_query, {"asset_id": asset_id})
            for member in members_result:
                asset_data["attached_to"]["members"].append({
                    "member_id": member.member_id,
                    "member_name": member.member_name
                })
        except:
            pass
        
        return asset_data

    def assets_search(self, asset_type: Optional[str] = None, q: Optional[str] = None,
                     mime_type: Optional[str] = None, project_id: Optional[int] = None,
                     blog_id: Optional[int] = None, member_id: Optional[int] = None,
                     limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Deep search of blogs in database based on keywords
        """
        # Start with base query
        from_clause = "FROM assets a"
        where_conditions = []
        params = {"limit": limit, "offset": offset}
        
        # Add joins based on filters
        if project_id:
            from_clause += " JOIN blog_assets ba ON ba.asset_id = a.asset_id JOIN blogs b ON b.blog_id = ba.blog_id"
            where_conditions.append("b.project_id = :project_id")
            params["project_id"] = project_id
            
        if blog_id:
            from_clause += " JOIN blog_assets ba ON ba.asset_id = a.asset_id"
            where_conditions.append("ba.blog_id = :blog_id")
            params["blog_id"] = blog_id
            
        if member_id:
            # Remove member_assets relationship since it doesn't exist in schema
            # from_clause += " JOIN member_assets ma ON ma.asset_id = a.asset_id"
            # where_conditions.append("ma.member_id = :member_id")
            # params["member_id"] = member_id
            pass
        
        # Add other filters
        if asset_type:
            where_conditions.append("a.asset_type = :asset_type")
            params["asset_type"] = asset_type
            
        if q:
            where_conditions.append("""
                (a.filename LIKE CONCAT('%', :q, '%') 
                 OR a.original_filename LIKE CONCAT('%', :q, '%')
                 OR a.description LIKE CONCAT('%', :q, '%'))
            """)
            params["q"] = q
            
        if mime_type:
            where_conditions.append("a.mime_type = :mime_type")
            params["mime_type"] = mime_type
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        query = text(f"""
            SELECT DISTINCT a.* 
            {from_clause}
            {where_clause}
            ORDER BY a.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        try:
            result = self.db.execute(query, params)
            assets = []
            for row in result:
                assets.append({
                    "asset_id": row.asset_id,
                    "filename": row.filename,
                    "original_filename": row.original_filename,
                    "cloudinary_url": row.cloudinary_url,
                    "asset_type": row.asset_type,
                    "file_size": row.file_size,
                    "mime_type": row.mime_type,
                    "youtube_video_id": row.youtube_video_id,
                    "description": row.description,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None
                })
            return assets
        except Exception as e:
            # Return basic assets if joins fail (tables don't exist)
            basic_query = text("""
                SELECT * FROM assets a
                WHERE (:asset_type IS NULL OR a.asset_type = :asset_type)
                  AND (:q IS NULL OR a.filename LIKE CONCAT('%', :q, '%') 
                       OR a.description LIKE CONCAT('%', :q, '%'))
                  AND (:mime_type IS NULL OR a.mime_type = :mime_type)
                ORDER BY a.created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            
            basic_params = {
                "asset_type": asset_type,
                "q": q,
                "mime_type": mime_type,
                "limit": limit,
                "offset": offset
            }
            
            result = self.db.execute(basic_query, basic_params)
            assets = []
            for row in result:
                assets.append({
                    "asset_id": row.asset_id,
                    "filename": row.filename,
                    "asset_type": row.asset_type,
                    "description": row.description,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })
            return assets


# Helper function to get tools instance
def get_mcp_tools() -> MCPTools:
    """Get MCPTools instance with database session"""
    db = get_db_session()
    return MCPTools(db)