# !/usr/bin/env python
# Copyright (C) 2025 HRForce
#
# All rights reserved.
# @link hrforce.ai
#
# __author__ = "man.tra@cvtot.vn"
# __date__ = "2025-09-24 11:26:49"
#

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from core.settings.base import settings

# Base for ORM models
Base = declarative_base()

DATABASE_URL = settings.DB_URL

engine = create_async_engine(
    DATABASE_URL, 
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

meta = sa.MetaData()


# Database dependency
async def get_db() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Create tables function
async def create_tables():
    """Create all database tables"""
    try:
        from core.db.db_schemas import (
            Project, Member, Blog, Asset, 
            AdminUser, AdminSession, ChatSession, ChatMessage, ToolCall,
            ProjectAsset, BlogAsset, MemberAsset
        )
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


# Test database connection
async def test_db_connection():
    """Test database connection"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(sa.text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection failed!")
                return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False