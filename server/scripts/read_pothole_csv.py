
import sys
import os
import boto3
import pandas as pd
from io import BytesIO

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

# This is the key we saw in the user's log
CSV_KEY = "1/pothole/846fa3cf-db56-4270-ba76-84623dfa4582.csv"

def check_csv():
    print(f"Downloading {CSV_KEY}...")
    s3 = boto3.client(
        service_name='s3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )
    
    try:
        obj = s3.get_object(Bucket=settings.R2_BUCKET_NAME, Key=CSV_KEY)
        df = pd.read_csv(BytesIO(obj['Body'].read()))
        
        print("CSV Columns:", df.columns.tolist())
        if 'image_path' in df.columns:
            print("First 5 image_path values:")
            print(df['image_path'].head())
            print("\nFirst 5 filenames from previous list script (for comparison):")
            print("00282298-2679-45bc-812c-b2097ac951eda.jpg") 
        else:
            print("image_path column missing!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_csv()
