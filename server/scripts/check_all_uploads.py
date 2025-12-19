
import sys
import os
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def check_uploads():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # Count by category
        result = conn.execute(text("""
            SELECT category, COUNT(*) as count 
            FROM uploads 
            GROUP BY category
            ORDER BY category
        """)).fetchall()
        
        print("=== Uploads by Category ===")
        total = 0
        for row in result:
            print(f"  {row[0]}: {row[1]} files")
            total += row[1]
        print(f"  TOTAL: {total} files")
        
        # Show recent uploads
        print("\n=== Last 5 Uploads ===")
        recent = conn.execute(text("""
            SELECT id, category, original_filename, upload_date 
            FROM uploads 
            ORDER BY upload_date DESC 
            LIMIT 5
        """)).fetchall()
        
        for row in recent:
            print(f"  ID:{row[0]} | {row[1]} | {row[2]} | {row[3]}")

if __name__ == "__main__":
    check_uploads()
