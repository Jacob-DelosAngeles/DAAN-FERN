
import sys
import os
import boto3

# Add parent directory to path so we can import core.config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

def clear_bucket():
    bucket_name = settings.R2_BUCKET_NAME
    print(f"Connecting to R2 Bucket: {bucket_name}...")
    
    s3 = boto3.resource(
        service_name='s3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )
    
    bucket = s3.Bucket(bucket_name)
    
    print("Listing and deleting all objects (this may take a moment)...")
    # Efficiently delete all objects
    # Note: versioned buckets require a different approach, but assuming standard here.
    try:
        bucket.objects.all().delete()
        print("All objects deleted successfully.")
    except Exception as e:
        print(f"Error deleting objects: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        clear_bucket()
    else:
        confirm = input("Are you sure you want to DELETE ALL FILES in the bucket? (yes/no): ")
        if confirm.lower() == "yes":
            clear_bucket()
        else:
            print("Operation cancelled.")
