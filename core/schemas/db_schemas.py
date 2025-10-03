"""
Strapi-like Database Schemas for PostgreSQL
Based on the DATABASE_SCHEMA_REPORT.md specification
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Create separate metadata and base for Strapi schema to avoid conflicts
strapi_metadata = MetaData()
StrapiBase = declarative_base(metadata=strapi_metadata)


# ==================== USERS & PERMISSIONS ====================

class UpUser(StrapiBase):
    """User table from users-permissions plugin"""
    __tablename__ = "up_users"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    password = Column(String(255), nullable=True)  # hashed password
    provider = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    blocked = Column(Boolean, default=False)
    reset_password_token = Column(String(255), nullable=True)
    confirmation_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)


# ==================== CONTENT TYPES ====================

class Blog(StrapiBase):
    """Blog content type"""
    __tablename__ = "blogs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)  # Rich text content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)
    
    # Relationships (using Strapi link tables)
    # Note: blogs_users_permissions_user_lnk table doesn't exist in current database
    projects = relationship("Project", secondary="blogs_project_lnk", back_populates="blogs", uselist=False)
    categories = relationship("Category", secondary="categories_blog_lnk", back_populates="blogs")
    authors = relationship("Author", secondary="authors_blog_lnk", back_populates="blogs")
    tags = relationship("Tag", secondary="blogs_tags_lnk", back_populates="blogs")


class Category(StrapiBase):
    """Category content type"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)

    blogs = relationship("Blog", secondary="categories_blog_lnk", back_populates="categories")


class Tag(StrapiBase):
    """Tag content type"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)

    blogs = relationship("Blog", secondary="blogs_tags_lnk", back_populates="tags")


class Author(StrapiBase):
    """Author content type"""
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)

    blogs = relationship("Blog", secondary="authors_blog_lnk", back_populates="authors")


class Project(StrapiBase):
    """Project content type"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)
    
    # Relationships (using Strapi link tables)
    technologies = relationship("Technology", secondary="projects_technologies_lnk", back_populates="projects")
    members = relationship("Member", secondary="members_projects_lnk", back_populates="projects")
    blogs = relationship("Blog", secondary="blogs_project_lnk", back_populates="projects")


class Technology(StrapiBase):
    """Technology content type"""
    __tablename__ = "technologies"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)

    projects = relationship("Project", secondary="projects_technologies_lnk", back_populates="technologies")


class Member(StrapiBase):
    """Member content type"""
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)  # Member bio/summary
    role = Column(String(100), nullable=True)
    team_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)

    projects = relationship("Project", secondary="members_projects_lnk", back_populates="members")



blogs_tags_lnk = Table(
    'blogs_tags_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('tag_id', Integer, ForeignKey('tags.id')),
    Column('blog_ord', Integer, nullable=True),
    Column('tag_ord', Integer, nullable=True)
)

projects_technologies_lnk = Table(
    'projects_technologies_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('technology_id', Integer, ForeignKey('technologies.id')),
    Column('project_ord', Integer, nullable=True),
    Column('technology_ord', Integer, nullable=True)
)

members_projects_lnk = Table(
    'members_projects_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('member_id', Integer, ForeignKey('members.id')),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('member_ord', Integer, nullable=True),
    Column('project_ord', Integer, nullable=True)
)

blogs_project_lnk = Table(
    'blogs_project_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('blog_ord', Integer, nullable=True),
    Column('project_ord', Integer, nullable=True)
)

categories_blog_lnk = Table(
    'categories_blog_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('category_ord', Integer, nullable=True),
    Column('blog_ord', Integer, nullable=True)
)

authors_blog_lnk = Table(
    'authors_blog_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id')),
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('author_ord', Integer, nullable=True),
    Column('blog_ord', Integer, nullable=True)
)

"""
Strapi-like Database Schemas for PostgreSQL
Based on the DATABASE_SCHEMA_REPORT.md specification
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Create separate metadata and base for Strapi schema to avoid conflicts
strapi_metadata = MetaData()
StrapiBase = declarative_base(metadata=strapi_metadata)


# ==================== USERS & PERMISSIONS ====================

class UpUser(StrapiBase):
    """User table from users-permissions plugin"""
    __tablename__ = "up_users"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    password = Column(String(255), nullable=True)  # hashed password
    provider = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    blocked = Column(Boolean, default=False)
    reset_password_token = Column(String(255), nullable=True)
    confirmation_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)


# ==================== CONTENT TYPES ====================

class Blog(StrapiBase):
    """Blog content type"""
    __tablename__ = "blogs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)  # Rich text content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)
    
    # Relationships (using Strapi link tables)
    # Note: blogs_users_permissions_user_lnk table doesn't exist in current database
    project = relationship("Project", secondary="blogs_project_lnk", backref="blogs", uselist=False)
    categories = relationship("Category", secondary="categories_blog_lnk", backref="blogs")
    authors = relationship("Author", secondary="authors_blog_lnk", backref="blogs")
    tags = relationship("Tag", secondary="blogs_tags_lnk", backref="blogs")


class Category(StrapiBase):
    """Category content type"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)


class Tag(StrapiBase):
    """Tag content type"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)


class Author(StrapiBase):
    """Author content type"""
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)


class Project(StrapiBase):
    """Project content type"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)
    
    # Relationships (using Strapi link tables)
    technologies = relationship("Technology", secondary="projects_technologies_lnk", backref="projects")
    members = relationship("Member", secondary="members_projects_lnk", backref="projects")


class Technology(StrapiBase):
    """Technology content type"""
    __tablename__ = "technologies"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)


class Member(StrapiBase):
    """Member content type"""
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)  # Member bio/summary
    role = Column(String(100), nullable=True)
    team_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    locale = Column(String(10), nullable=True)


# ==================== JOIN TABLES (Many-to-Many) - Strapi Link Tables ====================

# Strapi uses _lnk suffix for link tables
blogs_tags_lnk = Table(
    'blogs_tags_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('tag_id', Integer, ForeignKey('tags.id')),
    Column('blog_ord', Integer, nullable=True),
    Column('tag_ord', Integer, nullable=True)
)

projects_technologies_lnk = Table(
    'projects_technologies_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('technology_id', Integer, ForeignKey('technologies.id')),
    Column('project_ord', Integer, nullable=True),
    Column('technology_ord', Integer, nullable=True)
)

members_projects_lnk = Table(
    'members_projects_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('member_id', Integer, ForeignKey('members.id')),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('member_ord', Integer, nullable=True),
    Column('project_ord', Integer, nullable=True)
)

blogs_project_lnk = Table(
    'blogs_project_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('blog_ord', Integer, nullable=True),
    Column('project_ord', Integer, nullable=True)
)

categories_blog_lnk = Table(
    'categories_blog_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('category_ord', Integer, nullable=True),
    Column('blog_ord', Integer, nullable=True)
)

authors_blog_lnk = Table(
    'authors_blog_lnk',
    strapi_metadata,
    Column('id', Integer, primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id')),
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('author_ord', Integer, nullable=True),
    Column('blog_ord', Integer, nullable=True)
)
