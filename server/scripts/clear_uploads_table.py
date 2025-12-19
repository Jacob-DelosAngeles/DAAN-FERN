
import sys
import os
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def clear_tables():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        print("Clearing 'pothole_images' and 'uploads' tables...")
        # Cascade should handle it but explicit is safer
        connection.execute(text("TRUNCATE TABLE pothole_images, uploads RESTART IDENTITY CASCADE"))
        connection.commit()
        print("Tables cleared successfully.")

if __name__ == "__main__":
    clear_tables()
