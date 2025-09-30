"""
Repository for Member operations with Strapi schema
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.db.strapi_schemas import Member, Project


class StrapiMemberRepository:
    """Repository for member operations with Strapi schema"""
    
    @staticmethod
    async def get_member_by_id(
        db: AsyncSession,
        member_id: int,
        include_projects: bool = True
    ) -> Optional[Member]:
        """Get member by ID with optional projects"""
        if include_projects:
            result = await db.execute(
                select(Member)
                .options(selectinload(Member.projects))
                .where(Member.id == member_id)
            )
        else:
            result = await db.execute(select(Member).where(Member.id == member_id))
        
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_members(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        published_only: bool = False
    ) -> List[Member]:
        """Get all members with pagination"""
        query = select(Member).limit(limit).offset(offset)
        
        if published_only:
            query = query.where(Member.published_at.isnot(None))
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def search_members_by_keyword(
        db: AsyncSession,
        keyword: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Member]:
        """Search members by keyword in name, summary, or role"""
        like_pattern = f"%{keyword.lower()}%"
        result = await db.execute(
            select(Member)
            .where(
                (Member.name.ilike(like_pattern)) | 
                (Member.summary.ilike(like_pattern)) |
                (Member.role.ilike(like_pattern))
            )
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_members_by_team_type(
        db: AsyncSession,
        team_type: str,
        limit: int = 50
    ) -> List[Member]:
        """Get all members of a specific team type"""
        result = await db.execute(
            select(Member)
            .where(Member.team_type == team_type)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_members_by_role(
        db: AsyncSession,
        role: str,
        limit: int = 50
    ) -> List[Member]:
        """Get all members with a specific role"""
        result = await db.execute(
            select(Member)
            .where(Member.role == role)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create_member(
        db: AsyncSession,
        member_data: dict
    ) -> Member:
        """Create a new member"""
        member = Member(**member_data)
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member
    
    @staticmethod
    async def update_member(
        db: AsyncSession,
        member_id: int,
        member_data: dict
    ) -> Optional[Member]:
        """Update a member"""
        member = await StrapiMemberRepository.get_member_by_id(db, member_id, include_projects=False)
        if not member:
            return None
        
        for key, value in member_data.items():
            if hasattr(member, key):
                setattr(member, key, value)
        
        await db.commit()
        await db.refresh(member)
        return member
    
    @staticmethod
    async def delete_member(
        db: AsyncSession,
        member_id: int
    ) -> bool:
        """Delete a member"""
        member = await StrapiMemberRepository.get_member_by_id(db, member_id, include_projects=False)
        if not member:
            return False
        
        await db.delete(member)
        await db.commit()
        return True
