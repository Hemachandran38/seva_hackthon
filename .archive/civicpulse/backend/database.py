"""
database.py — SQLAlchemy engine and session factory.

Uses SQLite for the Phase 2 prototype.
Swap DATABASE_URL for a PostgreSQL connection string to migrate later:
  postgresql+psycopg2://user:password@host:5432/civicpulse
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite file stored in the backend directory
DATABASE_URL = "sqlite:///./civicpulse.db"

engine = create_engine(
    DATABASE_URL,
    # Required for SQLite to work correctly with multiple threads (FastAPI uses threads)
    connect_args={"check_same_thread": False},
)

# Each request gets its own session via the dependency in main.py
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()
