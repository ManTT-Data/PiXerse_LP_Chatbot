from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from core.db.base import Base


class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    project_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # # Relationships
    # members = relationship("Member", back_populates="project")
    # blogs = relationship("Blog", back_populates="project")


class Member(Base):
    __tablename__ = "members"
    
    member_id = Column(Integer, primary_key=True, index=True)
    member_name = Column(String(255), nullable=False)
    member_role = Column(String(255), nullable=False)
    team_type = Column(String(100)) 
    summary = Column(Text)  
    avatar_url = Column(String(500))  
    project_id = Column(Integer, ForeignKey("projects.project_id"))  
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # # Relationships
    # project = relationship("Project", back_populates="members")
    # blogs = relationship("Blog", back_populates="author")


class Blog(Base):
    __tablename__ = "blogs"
    
    blog_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True) 
    blog_title = Column(String(500), nullable=False)
    blog_content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("members.member_id"), nullable=False)
    category = Column(String(100)) 
    tags = Column(JSON)  
    featured_image = Column(String(500)) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # # Relationships
    # project = relationship("Project", back_populates="blogs")
    # author = relationship("Member", back_populates="blogs")
    # assets = relationship("Asset", secondary="blog_assets", back_populates="blogs")


class Asset(Base):
    __tablename__ = "assets"
    
    asset_id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255)) 
    cloudinary_public_id = Column(String(255)) 
    cloudinary_url = Column(String(500), nullable=False) 
    asset_type = Column(String(20), nullable=False) 
    file_size = Column(BigInteger, default=0) 
    mime_type = Column(String(100)) 
    youtube_video_id = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # # Relationships
    # blogs = relationship("Blog", secondary="blog_assets", back_populates="assets")


# class BlogAsset(Base):
#     __tablename__ = "blog_assets"
    
#     blog_id = Column(Integer, ForeignKey("blogs.blog_id"), primary_key=True)
#     asset_id = Column(Integer, ForeignKey("assets.asset_id"), primary_key=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
