from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.db.db_schemas import Member


class MemberRepository:

    @staticmethod
    async def get_member_by_id(
        db: AsyncSession,
        member_id: int,
    ) -> Optional[Member]:
        result = await db.execute(select(Member).where(Member.id == member_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_members_description(
        db: AsyncSession,
        status: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Member]:
        result = await db.execute(
            select(Member.member_name, Member.member_id, Member.summary)
            .limit(limit)
            .offset(offset),
        )
        return result.scalars().all()

    @staticmethod
    async def get_members_by_skill_keyword(
        db: AsyncSession,
        keyword: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Member]:
        like_pattern = f"%{keyword.lower()}%"
        result = await db.execute(
            select(Member)
            .where(Member.summary.ilike(like_pattern))
            .limit(limit)
            .offset(offset),
        )
        return result.scalars().all()