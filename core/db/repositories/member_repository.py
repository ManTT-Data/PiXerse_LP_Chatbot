"""
Repository for Member operations with Strapi schema
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.schemas.db_schemas import Member
from typing import Any, Mapping


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

        return result.unique().scalar_one_or_none()

    @staticmethod
    async def get_all_members_summary(
        db: AsyncSession,
        limit: int = 50
    ) -> list[Mapping[str, Any]]:
        """Get all members with pagination"""
        query = select(Member.id, Member.name, Member.summary, Member.role).limit(limit)

        result = await db.execute(query)
        return result.mappings().all()

    @staticmethod
    async def search_members_by_keyword(
        db: AsyncSession,
        keyword: str,
        limit: int = 50
    ) -> List[Member]:
        """Search members by keyword in name, summary, or role"""
        like_pattern = f"%{keyword.lower()}%"
        result = await db.execute(
            select(Member)
            .where(
                (Member.summary.ilike(like_pattern))
            )
            .limit(limit)
        )
        return result.unique().scalars().all()

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
        return result.unique().scalars().all()

    # @staticmethod
    # async def create_member(
    #     db: AsyncSession,
    #     member_data: dict
    # ) -> Member:
    #     """Create a new member"""
    #     member = Member(**member_data)
    #     db.add(member)
    #     await db.commit()
    #     await db.refresh(member)
    #     return member
    
    # @staticmethod
    # async def update_member(
    #     db: AsyncSession,
    #     member_id: int,
    #     member_data: dict
    # ) -> Optional[Member]:
    #     """Update a member"""
    #     member = await StrapiMemberRepository.get_member_by_id(db, member_id, include_projects=False)
    #     if not member:
    #         return None
        
    #     for key, value in member_data.items():
    #         if hasattr(member, key):
    #             setattr(member, key, value)
        
    #     await db.commit()
    #     await db.refresh(member)
    #     return member
    
    # @staticmethod
    # async def delete_member(
    #     db: AsyncSession,
    #     member_id: int
    # ) -> bool:
    #     """Delete a member"""
    #     member = await StrapiMemberRepository.get_member_by_id(db, member_id, include_projects=False)
    #     if not member:
    #         return False
        
    #     await db.delete(member)
    #     await db.commit()
    #     return True
