"""
Repository for Blog operations with Strapi schema
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.db.strapi_schemas import Blog, Tag, Category, Author


class StrapiBlogRepository:
    """Repository for blog operations with Strapi schema"""
    
    @staticmethod
    async def get_blog_by_id(
        db: AsyncSession,
        blog_id: int,
        include_relations: bool = True
    ) -> Optional[Blog]:
        """Get blog by ID with optional relations"""
        if include_relations:
            result = await db.execute(
                select(Blog)
                .options(
                    selectinload(Blog.users),
                    selectinload(Blog.project),
                    selectinload(Blog.tags),
                    selectinload(Blog.categories),
                    selectinload(Blog.authors)
                )
                .where(Blog.id == blog_id)
            )
        else:
            result = await db.execute(select(Blog).where(Blog.id == blog_id))
        
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_blogs(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        published_only: bool = False
    ) -> List[Blog]:
        """Get all blogs with pagination"""
        query = select(Blog).limit(limit).offset(offset)
        
        if published_only:
            query = query.where(Blog.published_at.isnot(None))
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def search_blogs_by_keyword(
        db: AsyncSession,
        keyword: str,
        limit: int = 50,
        offset: int = 0
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
            .offset(offset)
        )
        return list(result.scalars().all())
    
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
        return list(result.scalars().all())
    
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
        return list(result.scalars().all())
    
    @staticmethod
    async def create_blog(
        db: AsyncSession,
        blog_data: dict
    ) -> Blog:
        """Create a new blog"""
        blog = Blog(**blog_data)
        db.add(blog)
        await db.commit()
        await db.refresh(blog)
        return blog
    
    @staticmethod
    async def update_blog(
        db: AsyncSession,
        blog_id: int,
        blog_data: dict
    ) -> Optional[Blog]:
        """Update a blog"""
        blog = await StrapiBlogRepository.get_blog_by_id(db, blog_id, include_relations=False)
        if not blog:
            return None
        
        for key, value in blog_data.items():
            if hasattr(blog, key):
                setattr(blog, key, value)
        
        await db.commit()
        await db.refresh(blog)
        return blog
    
    @staticmethod
    async def delete_blog(
        db: AsyncSession,
        blog_id: int
    ) -> bool:
        """Delete a blog"""
        blog = await StrapiBlogRepository.get_blog_by_id(db, blog_id, include_relations=False)
        if not blog:
            return False
        
        await db.delete(blog)
        await db.commit()
        return True
