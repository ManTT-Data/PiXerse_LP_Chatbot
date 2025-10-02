from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, BigInteger, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from core.db.base import Base


# Enums
class AssetTypeEnum(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    YOUTUBE = "YOUTUBE"


class MessageRoleEnum(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


# Content Entities
class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("Member", back_populates="project")
    blogs = relationship("Blog", back_populates="project")
    # project_assets = relationship("ProjectAsset", back_populates="project")


class Member(Base):
    __tablename__ = "members"
    
    member_id = Column(Integer, primary_key=True, index=True)
    member_name = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True)
    team_type = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    experience = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    blogs = relationship("Blog", back_populates="author")
    # member_assets = relationship("MemberAsset", back_populates="member")


class Blog(Base):
    __tablename__ = "blogs"
    
    blog_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True)
    author_id = Column(Integer, ForeignKey("members.member_id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)
    featured_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="blogs")
    author = relationship("Member", back_populates="blogs")
    # blog_assets = relationship("BlogAsset", back_populates="blog")


class Asset(Base):
    __tablename__ = "assets"
    
    asset_id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    cloudinary_public_id = Column(String(255), nullable=True, unique=True, index=True)
    cloudinary_url = Column(Text, nullable=True)
    asset_type = Column(Enum(AssetTypeEnum), nullable=False)
    file_size = Column(BigInteger, nullable=True, default=0)
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    youtube_video_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # project_assets = relationship("ProjectAsset", back_populates="asset")
    # blog_assets = relationship("BlogAsset", back_populates="asset_id")
    # member_assets = relationship("MemberAsset", back_populates="asset")


# System Entities
class AdminUser(Base):
    __tablename__ = "admin_users"
    
    admin_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("AdminSession", back_populates="admin_user")


class AdminSession(Base):
    __tablename__ = "admin_sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.admin_id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="sessions")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    session_token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    message_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.session_id"), nullable=False)
    role = Column(Enum(MessageRoleEnum), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    tool_calls = relationship("ToolCall", back_populates="message")


class ToolCall(Base):
    __tablename__ = "tool_calls"
    
    tool_call_id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.message_id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    tool_input = Column(JSON, nullable=True)
    tool_output = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="tool_calls")


# Association Tables (M:N relationships)
class ProjectAsset(Base):
    __tablename__ = "project_assets"
    
    project_id = Column(Integer, ForeignKey("projects.project_id"), primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    # project = relationship("Project", back_populates="project_assets")
    # asset = relationship("Asset", back_populates="project_assets")


class BlogAsset(Base):
    __tablename__ = "blog_assets"
    
    blog_id = Column(Integer, ForeignKey("blogs.blog_id"), primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    # blog = relationship("Blog", back_populates="blog_assets")
    # asset = relationship("Asset", back_populates="blog_assets")


class MemberAsset(Base):
    __tablename__ = "member_assets"
    
    member_id = Column(Integer, ForeignKey("members.member_id"), primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    # member = relationship("Member", back_populates="member_assets")
    # asset = relationship("Asset", back_populates="member_assets")
