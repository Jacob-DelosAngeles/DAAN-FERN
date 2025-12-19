
import sys
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from models.upload import UploadModel

def test_transaction():
    print("--- Testing Database Deletion Transaction ---")
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # 1. Create a dummy "Zombie" record
    test_filename = f"zombie_test_{uuid.uuid4().hex[:8]}.jpg"
    print(f"1. Creating dummy record: {test_filename}")
    
    new_upload = UploadModel(
        user_id=1,
        filename=test_filename,
        original_filename=test_filename,
        file_type="jpg",
        category="pothole",
        storage_path=f"1/pothole/{test_filename}",
        file_size=123,
        file_hash="fakehash"
    )
    db.add(new_upload)
    db.commit()
    db.refresh(new_upload)
    
    record_id = new_upload.id
    print(f"   Created ID: {record_id}")
    
    # 2. Verify existence
    check1 = db.query(UploadModel).filter(UploadModel.id == record_id).first()
    if check1:
        print("   ✅ Record exists in DB.")
    else:
        print("   ❌ Failed to create record.")
        return

    # 3. Delete it
    print("2. Deleting record...")
    db.delete(check1)
    db.commit()
    print("   Commit executed.")
    
    # 4. Verify death
    # Create a NEW session to ensure no caching
    db.close()
    db2 = Session()
    
    print("3. Verifying deletion (New Session)...")
    check2 = db2.query(UploadModel).filter(UploadModel.id == record_id).first()
    
    if check2:
        print("   ❌ ZOMBIE DETECTED! Record still exists.")
    else:
        print("   ✅ Record successfully deleted.")
        
    db2.close()

if __name__ == "__main__":
    test_transaction()
