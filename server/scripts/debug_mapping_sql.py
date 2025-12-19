
import sys
import os
import boto3
import pandas as pd
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy import text # Use direct SQL to avoid ORM circular import issues

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def debug_mapping_raw_sql():
    print("--- Debugging Logic (Direct SQL) ---")
    
    engine = create_engine(settings.DATABASE_URL)
    connection = engine.connect()
    
    try:
        # 1. Find the latest Pothole CSV
        query = text("""
            SELECT user_id, filename, original_filename, storage_path 
            FROM uploads 
            WHERE category = 'pothole' AND file_type = 'csv' 
            ORDER BY upload_date DESC LIMIT 1
        """)
        result = connection.execute(query).fetchone()
        
        if not result:
            print("No Pothole CSV record found.")
            return

        user_id, filename, orig_filename, storage_path = result
        print(f"Latest CSV: {filename} (Original: {orig_filename})")
        print(f"User ID: {user_id}")
        
        # 2. Read content from R2
        print(f"Reading from R2: {storage_path}")
        s3 = boto3.client(
            service_name='s3',
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        )
        
        try:
            obj = s3.get_object(Bucket=settings.R2_BUCKET_NAME, Key=storage_path)
            content = obj['Body'].read()
            df = pd.read_csv(BytesIO(content))
        except Exception as e:
            print(f"Failed to read CSV from R2: {e}")
            return

        # 3. Get images from CSV
        if 'image_path' not in df.columns:
            print("Column 'image_path' missing in CSV.")
            return
            
        csv_images = df['image_path'].dropna().unique().tolist()
        print(f"Found {len(csv_images)} unique images in CSV.")
        if not csv_images:
            return

        sample_csv_image = csv_images[0]
        print(f"Sample CSV image: '{sample_csv_image}'")
        
        # 4. Check DB for this specific image
        # Use parameterized query
        img_query = text("""
            SELECT id, filename, original_filename, storage_path 
            FROM uploads 
            WHERE user_id = :uid AND category = 'pothole' AND original_filename = :fname
        """)
        
        print(f"Querying DB for: '{sample_csv_image}'")
        img_result = connection.execute(img_query, {"uid": user_id, "fname": sample_csv_image}).fetchone()
        
        if img_result:
             print("MATCH FOUND!")
             print(f"DB Record: {img_result}")
        else:
             print("NO MATCH FOUND.")
             
             # Debug: list all pothole images for this user
             print("\nListing ALL pothole images for this user in DB:")
             list_query = text("""
                 SELECT original_filename FROM uploads 
                 WHERE user_id = :uid AND category = 'pothole' AND file_type IN ('jpg', 'jpeg', 'png')
                 LIMIT 10
             """)
             rows = connection.execute(list_query, {"uid": user_id}).fetchall()
             for row in rows:
                 print(f" - '{row[0]}'")
                 if row[0].strip() == sample_csv_image.strip():
                      print("   (Wait, this string looks identical! Check whitespace/hidden chars?)")

    finally:
        connection.close()

if __name__ == "__main__":
    debug_mapping_raw_sql()
