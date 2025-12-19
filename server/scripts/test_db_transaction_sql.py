
import sys
import os
import uuid
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def test_transaction_sql():
    print("--- Testing Database Deletion (Direct SQL) ---")
    
    engine = create_engine(settings.DATABASE_URL)
    connection = engine.connect()
    
    # 1. Create a dummy "Zombie" record
    test_filename = f"zombie_test_{uuid.uuid4().hex[:8]}.jpg"
    print(f"1. Creating dummy record: {test_filename}")
    
    insert_query = text("""
        INSERT INTO uploads (user_id, filename, original_filename, file_type, category, storage_path, file_size, file_hash, upload_date)
        VALUES (1, :fname, :orig, 'jpg', 'pothole', :path, 123, 'fakehash', NOW())
        RETURNING id
    """)
    
    # SIMPLIFIED PATTERN
    verify_query = text("SELECT id FROM uploads WHERE id = :id")
    delete_query = text("DELETE FROM uploads WHERE id = :id")
    
    try:
        # Create
        connection.execute(insert_query, {
            "fname": test_filename, 
            "orig": test_filename,
            "path": f"1/pothole/{test_filename}"
        })
        connection.commit()
        
        # Get ID
        record_id = connection.execute(text("SELECT id FROM uploads WHERE filename=:f"), {"f": test_filename}).fetchone()[0]
        print(f"   Created ID: {record_id}")
        
        # Verify
        if connection.execute(verify_query, {"id": record_id}).fetchone():
            print("   ✅ Record exists.")
        
        # Delete
        print("2. Deleting record...")
        connection.execute(delete_query, {"id": record_id})
        connection.commit()
        print("   Commit executed.")
        
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # 4. Verify death
    print("3. Verifying deletion...")
    check2 = connection.execute(verify_query, {"id": record_id}).fetchone()
    
    if check2:
        print("   ❌ ZOMBIE DETECTED! Record still exists.")
    else:
        print("   ✅ Record successfully deleted.")
        
    connection.close()

if __name__ == "__main__":
    test_transaction_sql()
