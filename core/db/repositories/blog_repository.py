from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.db.db_schemas import Blog


class BlogRepository:

    @staticmethod
    async def get_blog_by_id(
        db: AsyncSession,
        blog_id: int,
    ) -> Optional[Blog]:
        result = await db.execute(select(Blog).where(Blog.blog_id == blog_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_blogs_description(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Blog]:
        result = await db.execute(
            select(Blog.blog_title, Blog.blog_id, Blog.blog_content)
            .limit(limit)
            .offset(offset),
        )
        return result.scalars().all()

    @staticmethod
    async def get_blogs_by_keywords(
        db: AsyncSession,
        keyword: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Blog]:
        like_pattern = f"%{keyword.lower()}%"
        result = await db.execute(
            select(Blog)
            .where(Blog.blog_content.ilike(like_pattern))
            .limit(limit)
            .offset(offset),
        )
        return result.scalars().all()