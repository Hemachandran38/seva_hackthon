"""
Database configuration and initialization for CivicPulse AI Backend.

This module handles SQLite database setup, session management, and 
initialization of database tables.
"""

import logging
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlmodel import SQLModel, Session, create_engine as sqlmodel_create_engine, select
from app.config import settings

logger = logging.getLogger(__name__)

# Ensure database directory exists
DB_PATH = Path(settings.database_url.replace("sqlite:///", ""))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create engine with SQLite-specific configurations
def get_engine():
    """Create and configure SQLAlchemy engine."""
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False}  # Required for SQLite with threading
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    return engine

engine = get_engine()

def get_session() -> Session:
    """Get database session for dependency injection."""
    from sqlmodel import Session as SQLModelSession
    session = SQLModelSession(engine)
    try:
        yield session
    finally:
        session.close()

def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)
    logger.info(f"Database initialized at {DB_PATH}")

def get_db_session():
    """Context manager for database sessions."""
    from sqlmodel import Session as SQLModelSession
    session = SQLModelSession(engine)
    try:
        yield session
    finally:
        session.close()
