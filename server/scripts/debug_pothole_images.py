
import sys
import os
import boto3
import pandas as pd
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from models.upload import UploadModel

def debug_pothole_data():
    print("--- Debugging Pothole Images ---")
    
    # 1. Connect to R2 and List Files in 1/pothole/
    print("\n1. Listing objects in '1/pothole/' (Limit 5):")
    s3 = boto3.client(
        service_name='s3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )
    
    try:
        response = s3.list_objects_v2(Bucket=settings.R2_BUCKET_NAME, Prefix="1/pothole/", MaxKeys=5)
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"   found: {obj['Key']}")
        else:
            print("   (No objects found in 1/pothole/)")
    except Exception as e:
        print(f"   Error listing objects: {e}")

    # 2. Check the CSV content for image_path column
    print("\n2. Checking 'pothole_detections.csv' (or similar) content:")
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Find the latest pothole CSV
    record = db.query(UploadModel).filter(
        UploadModel.category == 'pothole',
        UploadModel.file_type == 'csv'
    ).order_by(UploadModel.upload_date.desc()).first()
    
    if not record:
        print("   No pothole CSV record found in DB.")
        return

    print(f"   Found CSV Record: {record.filename} (Path: {record.storage_path})")
    
    try:
        # Download CSV
        obj = s3.get_object(Bucket=settings.R2_BUCKET_NAME, Key=record.storage_path)
        content = obj['Body'].read()
        df = pd.read_csv(BytesIO(content))
        
        if 'image_path' in df.columns:
            print("   'image_path' column first 5 values:")
            print(df['image_path'].head())
        else:
            print("   'image_path' column NOT found in CSV!")
            print(f"   Columns: {df.columns.tolist()}")
            
    except Exception as e:
        print(f"   Error reading CSV: {e}")

if __name__ == "__main__":
    debug_pothole_data()
