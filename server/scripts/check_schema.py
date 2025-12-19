"""Check current users table schema"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from core.database import engine

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND table_schema = 'public'
        ORDER BY ordinal_position
    """))
    print("Users table columns:")
    for row in result:
        print(f"  {row[0]}: {row[1]}")
