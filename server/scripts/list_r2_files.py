
import sys
import os
import boto3

# Add parent directory to path to import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def list_files():
    print(f"Bucket: {settings.R2_BUCKET_NAME}")
    print("Listing '1/pothole/'...")
    
    s3 = boto3.client(
        service_name='s3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )
    
    try:
        response = s3.list_objects_v2(Bucket=settings.R2_BUCKET_NAME, Prefix="1/pothole/", MaxKeys=10)
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f" - {obj['Key']} (Size: {obj['Size']})")
        else:
            print("No objects found in 1/pothole/")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_files()
