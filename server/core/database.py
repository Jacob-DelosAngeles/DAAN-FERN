from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# For PostgreSQL, use: "postgresql://user:password@postgresserver/db"

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL connection options for cross-region latency
    connect_args = {
        "connect_timeout": 10,           # Connection timeout in seconds
        "keepalives": 1,                 # Enable TCP keepalives
        "keepalives_idle": 30,           # Seconds before sending keepalive
        "keepalives_interval": 10,       # Interval between keepalives
        "keepalives_count": 5,           # Number of keepalives before giving up
    }

# Configure engine with optimized pool settings for Supabase
# Optimized for cross-region connections (Render US <-> Supabase Singapore)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args,
    poolclass=QueuePool,
    pool_pre_ping=True,           # Check if connection is alive before use
    pool_recycle=180,             # Recycle connections every 3 minutes
    pool_size=3,                  # Smaller pool size for free tier
    max_overflow=5,               # Allow extra connections during high load
    pool_timeout=30,              # Wait up to 30s for a connection from pool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Database session dependency.
    Creates a new session for each request and closes it when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

