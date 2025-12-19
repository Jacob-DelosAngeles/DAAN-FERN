
import sys
import os
import sqlalchemy
from sqlalchemy import create_engine, text

# Add parent directory to path so we can import core.config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

def migrate():
    print(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if column exists
        try:
            # PostgreSQL specific check
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='uploads' AND column_name='file_hash'"))
            if result.fetchone():
                print("Column 'file_hash' already exists.")
                return
        except Exception as e:
            print(f"Could not check column existence (might be SQLite?): {e}")

        # Add column
        print("Adding 'file_hash' column to 'uploads' table...")
        try:
            connection.execute(text("ALTER TABLE uploads ADD COLUMN file_hash VARCHAR"))
            connection.execute(text("CREATE INDEX ix_uploads_file_hash ON uploads (file_hash)"))
            connection.commit()
            print("Successfully added 'file_hash' column.")
        except Exception as e:
            print(f"Error adding column: {e}")
            # Try to rollback if possible, or just print error
            
if __name__ == "__main__":
    migrate()
