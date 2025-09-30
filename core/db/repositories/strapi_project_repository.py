"""
Repository for Project operations with Strapi schema
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.db.strapi_schemas import Project, Technology, Member


class StrapiProjectRepository:
    """Repository for project operations with Strapi schema"""
    
    @staticmethod
    async def get_project_by_id(
        db: AsyncSession,
        project_id: int,
        include_relations: bool = True
    ) -> Optional[Project]:
        """Get project by ID with optional relations"""
        if include_relations:
            result = await db.execute(
                select(Project)
                .options(
                    selectinload(Project.technologies),
                    selectinload(Project.members),
                    selectinload(Project.blogs)
                )
                .where(Project.id == project_id)
            )
        else:
            result = await db.execute(select(Project).where(Project.id == project_id))
        
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_projects(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        published_only: bool = False
    ) -> List[Project]:
        """Get all projects with pagination"""
        query = select(Project).limit(limit).offset(offset)
        
        if published_only:
            query = query.where(Project.published_at.isnot(None))
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def search_projects_by_keyword(
        db: AsyncSession,
        keyword: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Project]:
        """Search projects by keyword in name or description"""
        like_pattern = f"%{keyword.lower()}%"
        result = await db.execute(
            select(Project)
            .where(
                (Project.name.ilike(like_pattern)) | 
                (Project.description.ilike(like_pattern))
            )
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_projects_by_technology(
        db: AsyncSession,
        technology_id: int,
        limit: int = 50
    ) -> List[Project]:
        """Get all projects using a specific technology"""
        result = await db.execute(
            select(Project)
            .join(Project.technologies)
            .where(Technology.id == technology_id)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_projects_by_member(
        db: AsyncSession,
        member_id: int,
        limit: int = 50
    ) -> List[Project]:
        """Get all projects a member is part of"""
        result = await db.execute(
            select(Project)
            .join(Project.members)
            .where(Member.id == member_id)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create_project(
        db: AsyncSession,
        project_data: dict
    ) -> Project:
        """Create a new project"""
        project = Project(**project_data)
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project
    
    @staticmethod
    async def update_project(
        db: AsyncSession,
        project_id: int,
        project_data: dict
    ) -> Optional[Project]:
        """Update a project"""
        project = await StrapiProjectRepository.get_project_by_id(db, project_id, include_relations=False)
        if not project:
            return None
        
        for key, value in project_data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        await db.commit()
        await db.refresh(project)
        return project
    
    @staticmethod
    async def delete_project(
        db: AsyncSession,
        project_id: int
    ) -> bool:
        """Delete a project"""
        project = await StrapiProjectRepository.get_project_by_id(db, project_id, include_relations=False)
        if not project:
            return False
        
        await db.delete(project)
        await db.commit()
        return True
