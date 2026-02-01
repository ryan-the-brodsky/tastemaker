"""
Database configuration for TasteMaker.

Supports both SQLite (simple local use) and PostgreSQL (production).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import settings

# Get database URL from config
DATABASE_URL = settings.normalized_database_url

# Configure engine based on database type
if settings.is_sqlite:
    # SQLite requires check_same_thread=False for FastAPI
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL (or other databases)
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
