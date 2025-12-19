"""
Database Migration Script: Convert is_superuser to role

This script migrates the users table from:
- is_superuser (boolean) 

To:
- role (string: 'superuser', 'admin', 'user')

Run this script ONCE before starting the updated server.

Usage:
    cd server
    source venv/bin/activate  (Linux/Mac)
    python scripts/migrate_user_roles.py
"""

import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from core.database import engine, SessionLocal
from core.config import settings

def migrate_roles():
    """Migrate from is_superuser boolean to role string"""
    db = SessionLocal()
    
    try:
        print("Starting role migration...")
        print(f"Database: {settings.DATABASE_URL[:50]}...")
        
        with engine.connect() as conn:
            # Check current table structure
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND table_schema = 'public'
            """))
            columns = [row[0] for row in result]
            
            print(f"Current columns: {columns}")
            
            has_is_superuser = 'is_superuser' in columns
            has_role = 'role' in columns
            
            if has_role and not has_is_superuser:
                print("✅ Migration already complete (role column exists, is_superuser doesn't)")
                return
            
            if has_is_superuser and not has_role:
                print("📝 Need to add role column and migrate data...")
                
                # Add role column
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
                conn.commit()
                print("   Added 'role' column")
                
                # Migrate data: is_superuser=True -> role='superuser'
                # Use 'TRUE' for PostgreSQL compatibility
                conn.execute(text("UPDATE users SET role = 'superuser' WHERE is_superuser = TRUE"))
                conn.execute(text("UPDATE users SET role = 'user' WHERE is_superuser = FALSE OR is_superuser IS NULL"))
                conn.commit()
                print("   Migrated existing users' roles")
                
                print("   Note: is_superuser column kept for safety. You can remove it later.")
                print("✅ Migration complete!")
                
            elif has_is_superuser and has_role:
                print("📝 Both columns exist. Syncing data...")
                # Just sync the data
                conn.execute(text("UPDATE users SET role = 'superuser' WHERE is_superuser = TRUE AND (role IS NULL OR role = 'user')"))
                conn.commit()
                print("✅ Sync complete!")
            
            else:
                print("⚠️ Unexpected state. Manual inspection needed.")
                print(f"   has_is_superuser: {has_is_superuser}")
                print(f"   has_role: {has_role}")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        db.close()

def show_users():
    """Display current users and their roles"""
    db = SessionLocal()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, email, role FROM users ORDER BY id"))
            users = result.fetchall()
            
            print("\n📋 Current Users:")
            print("-" * 50)
            for user in users:
                print(f"   ID: {user[0]}, Email: {user[1]}, Role: {user[2]}")
            print("-" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("User Role Migration Script")
    print("=" * 50)
    
    migrate_roles()
    show_users()
    
    print("\n✨ Done! You can now start your server.")

