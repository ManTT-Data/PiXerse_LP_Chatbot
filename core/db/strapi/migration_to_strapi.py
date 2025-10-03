"""
Migration script to convert from old schema to Strapi-like schema
Run this script to migrate your database structure
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.db.meta import engine
from core.schemas.db_schemas import (
    StrapiBase, UpUser, Blog, Category, Tag, Author, Project, Technology, Member,
    blogs_tags_links, projects_technologies_links, members_projects_links
)
from core.log_handler import logger


async def backup_old_data():
    """Backup data from old schema"""
    logger.info("📦 Backing up old data...")
    
    async with AsyncSession(engine) as session:
        try:
            # Read old data
            result = await session.execute(text("SELECT * FROM projects"))
            old_projects = result.fetchall()
            
            result = await session.execute(text("SELECT * FROM members"))
            old_members = result.fetchall()
            
            result = await session.execute(text("SELECT * FROM blogs"))
            old_blogs = result.fetchall()
            
            logger.info(f"✅ Backed up {len(old_projects)} projects, {len(old_members)} members, {len(old_blogs)} blogs")
            
            return {
                'projects': old_projects,
                'members': old_members,
                'blogs': old_blogs
            }
        except Exception as e:
            logger.error(f"❌ Error backing up data: {e}")
            return None


async def drop_old_tables():
    """Drop old tables (CAUTION: This deletes all data!)"""
    logger.warning("⚠️ Dropping old tables...")
    
    async with engine.begin() as conn:
        try:
            # Drop old tables
            await conn.execute(text("DROP TABLE IF EXISTS tool_calls CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS chat_messages CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS chat_sessions CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS admin_sessions CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS admin_users CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS member_assets CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS blog_assets CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS project_assets CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS assets CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS blogs CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS members CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
            
            logger.info("✅ Old tables dropped successfully")
        except Exception as e:
            logger.error(f"❌ Error dropping tables: {e}")
            raise


async def create_strapi_tables():
    """Create new Strapi-like tables"""
    logger.info("🏗️ Creating Strapi schema tables...")
    
    async with engine.begin() as conn:
        try:
            await conn.run_sync(StrapiBase.metadata.create_all)
            logger.info("✅ Strapi tables created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
            raise


async def migrate_data(backup_data: dict):
    """Migrate data from old schema to new Strapi schema"""
    if not backup_data:
        logger.warning("⚠️ No backup data to migrate")
        return
    
    logger.info("🔄 Migrating data to new schema...")
    
    async with AsyncSession(engine) as session:
        try:
            # Migrate Projects
            for old_project in backup_data['projects']:
                new_project = Project(
                    id=old_project.project_id if hasattr(old_project, 'project_id') else old_project[0],
                    name=old_project.project_name if hasattr(old_project, 'project_name') else old_project[1],
                    description=old_project.description if hasattr(old_project, 'description') else old_project[2],
                    url=None,
                    published_at=old_project.created_at if hasattr(old_project, 'created_at') else None,
                )
                session.add(new_project)
            
            # Migrate Members
            for old_member in backup_data['members']:
                new_member = Member(
                    id=old_member.member_id if hasattr(old_member, 'member_id') else old_member[0],
                    name=old_member.member_name if hasattr(old_member, 'member_name') else old_member[1],
                    summary=old_member.summary if hasattr(old_member, 'summary') else None,
                    role=old_member.role if hasattr(old_member, 'role') else None,
                    team_type=old_member.team_type if hasattr(old_member, 'team_type') else None,
                    published_at=old_member.created_at if hasattr(old_member, 'created_at') else None,
                )
                session.add(new_member)
            
            # Migrate Blogs
            for old_blog in backup_data['blogs']:
                new_blog = Blog(
                    id=old_blog.blog_id if hasattr(old_blog, 'blog_id') else old_blog[0],
                    title=old_blog.title if hasattr(old_blog, 'title') else None,
                    content=old_blog.content if hasattr(old_blog, 'content') else None,
                    featured_image=old_blog.featured_image if hasattr(old_blog, 'featured_image') else None,
                    project_id=old_blog.project_id if hasattr(old_blog, 'project_id') else None,
                    users_permissions_user_id=None,  # Will need manual assignment
                    published_at=old_blog.created_at if hasattr(old_blog, 'created_at') else None,
                )
                session.add(new_blog)
            
            await session.commit()
            logger.info(f"✅ Migrated {len(backup_data['projects'])} projects, {len(backup_data['members'])} members, {len(backup_data['blogs'])} blogs")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Error migrating data: {e}")
            raise


async def create_sample_data():
    """Create sample data for testing"""
    logger.info("📝 Creating sample data...")
    
    async with AsyncSession(engine) as session:
        try:
            # Create sample user
            sample_user = UpUser(
                username="admin",
                email="admin@pixerse.com",
                password="hashed_password_here",
                confirmed=True,
                blocked=False
            )
            session.add(sample_user)
            await session.flush()
            
            # Create sample project
            sample_project = Project(
                name="PiXerse Portfolio",
                description="Official portfolio website of PiXerse team",
                url="https://pixerse.com",
                published_at=None
            )
            session.add(sample_project)
            await session.flush()
            
            # Create sample technologies
            tech_python = Technology(name="Python", published_at=None)
            tech_fastapi = Technology(name="FastAPI", published_at=None)
            tech_react = Technology(name="React", published_at=None)
            session.add_all([tech_python, tech_fastapi, tech_react])
            await session.flush()
            
            # Create sample members
            member1 = Member(
                name="John Doe",
                summary="Full-stack developer with 5 years of experience",
                role="Senior Developer",
                team_type="Development",
                published_at=None
            )
            member2 = Member(
                name="Jane Smith",
                summary="UI/UX designer specializing in modern web design",
                role="Lead Designer",
                team_type="Design",
                published_at=None
            )
            session.add_all([member1, member2])
            await session.flush()
            
            # Create sample blog
            sample_blog = Blog(
                title="Welcome to PiXerse Blog",
                content="This is our first blog post about our amazing team and projects!",
                featured_image="https://example.com/image.jpg",
                users_permissions_user_id=sample_user.id,
                project_id=sample_project.id,
                published_at=None
            )
            session.add(sample_blog)
            await session.flush()
            
            # Create sample tags and categories
            tag1 = Tag(name="Tutorial", published_at=None)
            tag2 = Tag(name="News", published_at=None)
            session.add_all([tag1, tag2])
            await session.flush()
            
            category1 = Category(name="Technology", blog_id=sample_blog.id, published_at=None)
            session.add(category1)
            
            await session.commit()
            logger.info("✅ Sample data created successfully")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Error creating sample data: {e}")
            raise


async def run_migration(create_samples: bool = True):
    """
    Main migration function
    
    Args:
        create_samples: Whether to create sample data after migration
    """
    logger.info("🚀 Starting migration to Strapi schema...")
    
    try:
        # Step 1: Backup old data
        backup_data = await backup_old_data()
        
        # Step 2: Drop old tables
        await drop_old_tables()
        
        # Step 3: Create new Strapi tables
        await create_strapi_tables()
        
        # Step 4: Migrate data if backup exists
        if backup_data:
            await migrate_data(backup_data)
        
        # Step 5: Create sample data if requested
        if create_samples:
            await create_sample_data()
        
        logger.info("✅ Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


async def rollback_migration():
    """Rollback migration (recreate old schema)"""
    logger.warning("🔄 Rolling back migration...")
    
    try:
        # Import old schemas
        from core.db.base import Base as OldBase
        
        async with engine.begin() as conn:
            # Drop Strapi tables
            await conn.run_sync(StrapiBase.metadata.drop_all)
            # Recreate old tables
            await conn.run_sync(OldBase.metadata.create_all)
        
        logger.info("✅ Rollback completed successfully")
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        asyncio.run(rollback_migration())
    else:
        # Run migration with sample data
        asyncio.run(run_migration(create_samples=True))
