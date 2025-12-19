from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# For PostgreSQL, use: "postgresql://user:password@postgresserver/db"

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Configure engine with connection pool settings for Supabase
# pool_pre_ping: Test connections before using (detects stale connections)
# pool_recycle: Recycle connections every 5 minutes (Supabase may drop idle ones)
# pool_size: Limit active connections
# max_overflow: Allow extra connections during high load
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,           # Check if connection is alive before use
    pool_recycle=300,             # Recycle connections every 5 minutes
    pool_size=5,                  # Default pool size
    max_overflow=10,              # Allow up to 10 extra connections
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

