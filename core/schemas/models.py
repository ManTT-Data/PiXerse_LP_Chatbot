from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Project(Base):
    """Project model - Bảng projects"""
    __tablename__ = "projects"
    
    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    project_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("Member", back_populates="project")
    blogs = relationship("Blog", back_populates="project")


class Member(Base):
    """Member model - Bảng members"""
    __tablename__ = "members"
    
    member_id = Column(Integer, primary_key=True, index=True)
    member_name = Column(String(255), nullable=False)
    member_role = Column(String(255), nullable=False)
    team_type = Column(String(100))  # Tech, Design, Marketing
    summary = Column(Text)  # Mô tả ngắn gọn cho AI
    avatar_url = Column(String(500))  # Link ảnh đại diện
    project_id = Column(Integer, ForeignKey("projects.project_id"))  # Dự án chính hiện tại
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    blogs = relationship("Blog", back_populates="author")


class Blog(Base):
    """Blog model - Bảng blogs"""
    __tablename__ = "blogs"
    
    blog_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True)  # Có thể NULL
    blog_title = Column(String(500), nullable=False)
    blog_content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("members.member_id"), nullable=False)
    category = Column(String(100))  # tutorial, news, showcase
    tags = Column(JSON)  # Dạng JSON, lưu mảng tag
    featured_image = Column(String(500))  # Hình ảnh đại diện
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="blogs")
    author = relationship("Member", back_populates="blogs")
    assets = relationship("Asset", secondary="blog_assets", back_populates="blogs")


class Asset(Base):
    """Asset model - Bảng assets"""
    __tablename__ = "assets"
    
    asset_id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))  # Tên gốc
    cloudinary_public_id = Column(String(255))  # ID trong Cloudinary
    cloudinary_url = Column(String(500), nullable=False)  # URL Cloudinary hoặc YouTube
    asset_type = Column(String(20), nullable=False)  # IMAGE, VIDEO, YOUTUBE
    file_size = Column(BigInteger, default=0)  # Dung lượng file (0 nếu YouTube)
    mime_type = Column(String(100))  # Kiểu MIME
    youtube_video_id = Column(String(50))  # ID video YouTube
    description = Column(Text)  # Mô tả/alt text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    blogs = relationship("Blog", secondary="blog_assets", back_populates="assets")


class BlogAsset(Base):
    """BlogAsset model - Bảng trung gian blog_assets"""
    __tablename__ = "blog_assets"
    
    blog_id = Column(Integer, ForeignKey("blogs.blog_id"), primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
