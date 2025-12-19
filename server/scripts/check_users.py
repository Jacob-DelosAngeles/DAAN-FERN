
import sys
import os
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def check_users():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, email, is_superuser FROM users")).fetchall()
        print(f"Total Users: {len(result)}")
        for row in result:
            print(f" - ID: {row[0]}, Email: {row[1]}")

if __name__ == "__main__":
    check_users()
