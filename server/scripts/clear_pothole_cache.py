import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent))

from sqlalchemy import create_engine, text
from core.config import settings

def clear_pothole_cache():
    """
    Clears the cached_data for all pothole CSV uploads in the database.
    This forces the backend to re-calculate URLs using the current R2 configuration.
    """
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Update statement to clear cache for pothole CSVs
        query = text("""
            UPDATE uploads 
            SET cached_data = NULL 
            WHERE category = 'pothole' AND file_type = 'csv';
        """)
        
        result = connection.execute(query)
        connection.commit()
        
        print(f"✅ Cache cleared! Affected rows: {result.rowcount}")
        print("Pothole data will be re-processed on next request using the active R2_PUBLIC_URL.")

if __name__ == "__main__":
    confirm = input("This will clear the cache for ALL pothole uploads. Continue? (y/n): ")
    if confirm.lower() == 'y':
        clear_pothole_cache()
    else:
        print("Operation cancelled.")
