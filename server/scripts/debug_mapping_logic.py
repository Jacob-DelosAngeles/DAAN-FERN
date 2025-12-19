
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

def debug_mapping():
    print("--- Debugging CSV <-> DB Mapping ---")
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # 1. Find the latest Pothole CSV
    csv_record = db.query(UploadModel).filter(
        UploadModel.category == 'pothole',
        UploadModel.file_type == 'csv'
    ).order_by(UploadModel.upload_date.desc()).first()
    
    if not csv_record:
        print("No Pothole CSV found.")
        return

    print(f"Latest CSV: {csv_record.filename} (Original: {csv_record.original_filename})")
    
    # 2. Read content
    print(f"Reading from R2: {csv_record.storage_path}")
    s3 = boto3.client(
        service_name='s3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )
    
    try:
        obj = s3.get_object(Bucket=settings.R2_BUCKET_NAME, Key=csv_record.storage_path)
        df = pd.read_csv(BytesIO(obj['Body'].read()))
    except Exception as e:
        print(f"Failed to read CSV from R2: {e}")
        return

    # 3. Get images from CSV
    if 'image_path' not in df.columns:
        print("Column 'image_path' missing in CSV.")
        return
        
    csv_images = df['image_path'].dropna().unique().tolist()
    print(f"Found {len(csv_images)} unique images in CSV.")
    print(f"Sample CSV images: {csv_images[:3]}")
    
    # 4. Query DB for these images
    user_id = csv_record.user_id
    print(f"Querying DB for images (User ID: {user_id}, Category: pothole)...")
    
    # Check what file types are actually in DB
    all_pothole_images = db.query(UploadModel).filter(
        UploadModel.user_id == user_id,
        UploadModel.category == 'pothole',
        UploadModel.file_type != 'csv'
    ).all()
    
    print(f"Total pothole images in DB: {len(all_pothole_images)}")
    if all_pothole_images:
        print(f"Sample DB original_filenames: {[img.original_filename for img in all_pothole_images[:3]]}")
    
    # 5. Check intersection
    matches = db.query(UploadModel).filter(
        UploadModel.user_id == user_id,
        UploadModel.category == 'pothole',
        UploadModel.original_filename.in_(csv_images)
    ).all()
    
    print(f"MATCHES FOUND: {len(matches)}")
    
    if len(matches) == 0 and len(csv_images) > 0 and len(all_pothole_images) > 0:
        print("\n--- MISMATCH ANALYSIS ---")
        csv_first = csv_images[0]
        print(f"CSV Header: '{csv_first}' (Type: {type(csv_first)})")
        
        # Find potential candidate
        candidate = next((img for img in all_pothole_images if img.original_filename.strip() == csv_first.strip()), None)
        if candidate:
            print(f"Found candidate match but equality failed!")
            print(f"DB: '{candidate.original_filename}'")
            print(f"CSV: '{csv_first}'")
        else:
            print("No close match found for first item.")

if __name__ == "__main__":
    debug_mapping()
