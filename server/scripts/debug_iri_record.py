
import sys
import os
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from models.upload import UploadModel
from models.user import UserModel

FILENAME = "45f841b7-ec02-4eb0-a228-628676cadae9.csv"

def debug_file():
    print(f"Checking DB for: {FILENAME}")
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Check DB
    record = db.query(UploadModel).filter(
        (UploadModel.filename == FILENAME) | (UploadModel.original_filename == FILENAME)
    ).first()
    
    if not record:
        print("!! Record NOT found in Database !!")
        return

    print(f"Record Found!")
    print(f"ID: {record.id}")
    print(f"Storage Path: '{record.storage_path}'")
    print(f"User ID: {record.user_id}")
    
    # Check R2
    print(f"\nAttempting to fetch from R2 using key: '{record.storage_path}'")
    s3 = boto3.client(
        service_name='s3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )
    
    try:
        s3.head_object(Bucket=settings.R2_BUCKET_NAME, Key=record.storage_path)
        print("SUCCESS: Object exists in R2.")
    except Exception as e:
        print(f"FAILURE: R2 Error: {e}")
        
        # List bucket to see what's actually there
        print("\nListing first 10 items in bucket:")
        try:
             response = s3.list_objects_v2(Bucket=settings.R2_BUCKET_NAME, MaxKeys=10)
             if 'Contents' in response:
                 for obj in response['Contents']:
                     print(f" - {obj['Key']}")
             else:
                 print("Bucket is empty.")
        except Exception as le:
            print(f"List error: {le}")

if __name__ == "__main__":
    debug_file()
