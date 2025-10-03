"""
Repository for Project operations with Strapi schema
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.schemas.db_schemas import Project
from typing import Any, Mapping


class StrapiProjectRepository:
    """Repository for project operations with Strapi schema"""
    
    @staticmethod
    async def get_project_by_id(
        db: AsyncSession,
        project_id: int
    ) -> Optional[Project]:
        """Get project by ID with optional relations"""
        result = await db.execute(
            select(Project)
            .options(
                selectinload(Project.technologies),
                selectinload(Project.members),
                selectinload(Project.blogs)
            )
            .where(Project.id == project_id)
        )
        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def get_all_projects_description(
        db: AsyncSession,
        limit: int = 50
    ) -> list[Mapping[str, Any]]:
        """Get all projects with pagination"""
        query = select(Project.id, Project.name, Project.description).limit(limit)

        result = await db.execute(query)
        return result.mappings().all()

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
        return result.unique().scalars().all()

    # @staticmethod
    # async def get_projects_by_member(
    #     db: AsyncSession,
    #     member_id: int,
    #     limit: int = 50
    # ) -> List[Project]:
    #     """Get all projects a member is part of"""
    #     result = await db.execute(
    #         select(Project)
    #         .join(Project.members)
    #         .where(Member.id == member_id)
    #         .limit(limit)
    #     )
    #     return list(result.scalars().all())
    
    # @staticmethod
    # async def create_project(
    #     db: AsyncSession,
    #     project_data: dict
    # ) -> Project:
    #     """Create a new project"""
    #     project = Project(**project_data)
    #     db.add(project)
    #     await db.commit()
    #     await db.refresh(project)
    #     return project
    
    # @staticmethod
    # async def update_project(
    #     db: AsyncSession,
    #     project_id: int,
    #     project_data: dict
    # ) -> Optional[Project]:
    #     """Update a project"""
    #     project = await StrapiProjectRepository.get_project_by_id(db, project_id, include_relations=False)
    #     if not project:
    #         return None
        
    #     for key, value in project_data.items():
    #         if hasattr(project, key):
    #             setattr(project, key, value)
        
    #     await db.commit()
    #     await db.refresh(project)
    #     return project
    
    # @staticmethod
    # async def delete_project(
    #     db: AsyncSession,
    #     project_id: int
    # ) -> bool:
    #     """Delete a project"""
    #     project = await StrapiProjectRepository.get_project_by_id(db, project_id, include_relations=False)
    #     if not project:
    #         return False
        
    #     await db.delete(project)
    #     await db.commit()
    #     return True
