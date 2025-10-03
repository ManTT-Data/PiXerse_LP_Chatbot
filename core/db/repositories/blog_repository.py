"""
Repository for Blog operations with Strapi schema
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.schemas.db_schemas import Blog, Tag
from typing import Any, Mapping


class StrapiBlogRepository:
    """Repository for blog operations with Strapi schema"""
    
    @staticmethod
    async def get_blog_by_id(
        db: AsyncSession,
        blog_id: int
    ) -> Optional[Blog]:
        """Get blog by ID with optional relations"""
        result = await db.execute(
            select(Blog)
            .options(
                selectinload(Blog.project),
                selectinload(Blog.tags),
                selectinload(Blog.categories),
                selectinload(Blog.authors)
            )
            .where(Blog.id == blog_id)
        )

        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def get_all_blogs_content(
        db: AsyncSession,
        limit: int = 50
    ) -> list[Mapping[str, Any]]:
        """Get all blogs with pagination"""
        query = select(Blog.id, Blog.title, Blog.content).limit(limit)

        result = await db.execute(query)
        return result.mappings().all()

    @staticmethod
    async def search_blogs_by_keyword(
        db: AsyncSession,
        keyword: str,
        limit: int = 50
    ) -> List[Blog]:
        """Search blogs by keyword in title or content"""
        like_pattern = f"%{keyword.lower()}%"
        result = await db.execute(
            select(Blog)
            .where(
                (Blog.title.ilike(like_pattern)) |
                (Blog.content.ilike(like_pattern))
            )
            .limit(limit)
        )
        return result.unique().scalars().all()
    
    @staticmethod
    async def get_blogs_by_project(
        db: AsyncSession,
        project_id: int,
        limit: int = 50
    ) -> List[Blog]:
        """Get all blogs for a specific project"""
        result = await db.execute(
            select(Blog)
            .where(Blog.project_id == project_id)
            .limit(limit)
        )
        return result.unique().scalars().all()

    @staticmethod
    async def get_blogs_by_tag(
        db: AsyncSession,
        tag_id: int,
        limit: int = 50
    ) -> List[Blog]:
        """Get all blogs with a specific tag"""
        result = await db.execute(
            select(Blog)
            .join(Blog.tags)
            .where(Tag.id == tag_id)
            .limit(limit)
        )
        return result.unique().scalars().all()

    # @staticmethod
    # async def create_blog(
    #     db: AsyncSession,
    #     blog_data: dict
    # ) -> Blog:
    #     """Create a new blog"""
    #     blog = Blog(**blog_data)
    #     db.add(blog)
    #     await db.commit()
    #     await db.refresh(blog)
    #     return blog
    
    # @staticmethod
    # async def update_blog(
    #     db: AsyncSession,
    #     blog_id: int,
    #     blog_data: dict
    # ) -> Optional[Blog]:
    #     """Update a blog"""
    #     blog = await StrapiBlogRepository.get_blog_by_id(db, blog_id, include_relations=False)
    #     if not blog:
    #         return None
        
    #     for key, value in blog_data.items():
    #         if hasattr(blog, key):
    #             setattr(blog, key, value)
        
    #     await db.commit()
    #     await db.refresh(blog)
    #     return blog
    
    # @staticmethod
    # async def delete_blog(
    #     db: AsyncSession,
    #     blog_id: int
    # ) -> bool:
    #     """Delete a blog"""
    #     blog = await StrapiBlogRepository.get_blog_by_id(db, blog_id, include_relations=False)
    #     if not blog:
    #         return False
        
    #     await db.delete(blog)
    #     await db.commit()
    #     return True
