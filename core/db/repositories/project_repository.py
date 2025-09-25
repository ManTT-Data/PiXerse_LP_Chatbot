from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.db.db_schemas import Project


class ProjectRepository:

    @staticmethod
    async def get_project_by_id(
        db: AsyncSession,
        project_id: int,
    ) -> Optional[Project]:
        result = await db.execute(select(Project).where(Project.project_id == project_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_projects_description(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Project]:
        result = await db.execute(
            select(Project.project_name, Project.project_id, Project.project_description)
            .limit(limit)
            .offset(offset),
        )
        return result.scalars().all()

    @staticmethod
    async def get_projects_by_keywords(
        db: AsyncSession,
        keyword: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Project]:
        like_pattern = f"%{keyword.lower()}%"
        result = await db.execute(
            select(Project)
            .where(Project.project_description.ilike(like_pattern))
            .limit(limit)
            .offset(offset),
        )
        return result.scalars().all()