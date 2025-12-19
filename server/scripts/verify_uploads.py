
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from models.upload import UploadModel
from models.user import UserModel # Import to ensure relationships are set

def verify():
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    count = db.query(UploadModel).count()
    print(f"Total Uploads in DB: {count}")
    
    if count > 0:
        last = db.query(UploadModel).order_by(UploadModel.id.desc()).first()
        print(f"Last Upload: {last.filename}")
        print(f"Storage Path: {last.storage_path}")
        print(f"File Hash: {last.file_hash}")
        print(f"File Size: {last.file_size}")

if __name__ == "__main__":
    verify()
