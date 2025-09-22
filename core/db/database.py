from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from core.settings.base import settings

# Create SQLAlchemy engine with SSL support for cloud databases
engine_kwargs = {
    "echo": settings.debug,
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 5,
    "max_overflow": 10
}

# Add SSL configuration for cloud databases (like Aiven)
if "sslmode=require" in settings.database_url:
    engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(settings.database_url, **engine_kwargs)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


def get_db():
    """Dependency to get database session (for FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session (for MCP tools)"""
    return SessionLocal()


def create_tables():
    """Create all tables"""
    from core.schemas.models import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables"""
    from core.schemas.models import Base
    Base.metadata.drop_all(bind=engine)