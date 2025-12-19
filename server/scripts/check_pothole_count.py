
import sys
import os
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def check_count():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM uploads WHERE category = 'pothole'")).fetchone()
        print(f"Pothole Uploads Count: {result[0]}")

if __name__ == "__main__":
    check_count()
