#!/usr/bin/env python3
"""
Migration script to add cache columns to uploads table.
Run this once after deploying the new code.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from sqlalchemy import text

def migrate():
    print("Adding cache columns to uploads table...")
    
    with engine.connect() as conn:
        # Check if columns already exist
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'uploads' AND column_name = 'cached_data'
        """))
        
        if result.fetchone():
            print("Cache columns already exist. Skipping.")
            return
        
        # Add the new columns
        try:
            conn.execute(text("""
                ALTER TABLE uploads 
                ADD COLUMN cached_data TEXT,
                ADD COLUMN cache_timestamp TIMESTAMP
            """))
            conn.commit()
            print("✅ Successfully added cache columns!")
        except Exception as e:
            print(f"Error adding columns: {e}")
            # Try individual columns (in case one exists)
            try:
                conn.execute(text("ALTER TABLE uploads ADD COLUMN cached_data TEXT"))
                conn.commit()
            except:
                pass
            try:
                conn.execute(text("ALTER TABLE uploads ADD COLUMN cache_timestamp TIMESTAMP"))
                conn.commit()
            except:
                pass
            print("✅ Columns added (with individual fallback)")

if __name__ == "__main__":
    migrate()
