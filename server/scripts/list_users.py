import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.user import UserModel

def list_users():
    db = SessionLocal()
    try:
        users = db.query(UserModel).all()
        if not users:
            print("No users found in database.")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Admin: {user.is_superuser}, Active: {user.is_active}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
