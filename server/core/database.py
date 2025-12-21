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
    # PostgreSQL connection options - aggressive settings for Supabase cold starts
    connect_args = {
        "connect_timeout": 30,           # Connection timeout - allow 30s for cold start
        "keepalives": 1,                 # Enable TCP keepalives
        "keepalives_idle": 10,           # Seconds before sending keepalive (reduced)
        "keepalives_interval": 5,        # Interval between keepalives (reduced)
        "keepalives_count": 10,          # Number of keepalives before giving up
        "options": "-c statement_timeout=60000"  # 60s statement timeout
    }

# Configure engine with optimized pool settings for Supabase
# Optimized for cross-region connections with cold-start handling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args,
    poolclass=QueuePool,
    pool_pre_ping=True,           # Check if connection is alive before use
    pool_recycle=60,              # Recycle connections every 1 minute (more aggressive)
    pool_size=2,                  # Smaller pool for faster pre-ping
    max_overflow=3,               # Limited overflow
    pool_timeout=60,              # Wait up to 60s for a connection from pool
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

