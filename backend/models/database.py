"""
Database connection and session management.
Uses SQLAlchemy for ORM functionality with MySQL backend.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

# Create database engine
engine = create_engine(
    config.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=config.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


class Interaction(Base):
    """
    Interaction model for storing HCP interaction logs.
    
    Fields:
    - id: Unique identifier
    - doctor_name: Name of the healthcare professional
    - summary: AI-extracted summary of the interaction
    - sentiment: Sentiment analysis (positive/neutral/negative)
    - follow_up: Follow-up date or notes
    - created_at: Timestamp of creation
    - interaction_text: Raw interaction text from conversation
    """
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String(255), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    sentiment = Column(String(50), default="neutral")  # positive, neutral, negative
    follow_up = Column(Text, nullable=True)
    interaction_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


def get_db():
    """
    Dependency function to get database session.
    Used in FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Call this once at application startup.
    """
    Base.metadata.create_all(bind=engine)
