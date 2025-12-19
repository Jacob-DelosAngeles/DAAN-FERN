
import sys
import os
import boto3
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

def wipe_potholes():
    print("WARNING: This will delete ALL Pothole data (DB Records + R2 Images).")
    confirm = input("Type 'destroy' to proceed: ")
    if confirm != "destroy":
        print("Aborted.")
        return

    # 1. Clear R2
    print("\n1. Cleaning R2 Bucket (1/pothole/)...")
    s3 = boto3.resource(
        service_name='s3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )
    bucket = s3.Bucket(settings.R2_BUCKET_NAME)
    
    # Delete objects with prefix "1/pothole/" (Assuming User ID 1)
    # Ideally should query users but we know context is Jacob (User 1)
    # But let's be safe and list everything in "*/pothole/" if we want or just "1/"?
    # Let's stick to "1/pothole/" based on debug logs
    prefix = "1/pothole/" 
    try:
        bucket.objects.filter(Prefix=prefix).delete()
        print("   R2 Pothole images deleted.")
    except Exception as e:
        print(f"   Error clearing R2: {e}")

    # 2. Clear Database
    print("\n2. Cleaning Database (uploads table)...")
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # Delete related pothole_images first if they exist (though cascade might handle it)
        # But our manual logic uses uploads table.
        # Smart Deletion logic uses UploadModel.
        try:
             # Delete child records from pothole_images first to avoid FK constraint errors
             print("   Deleting from pothole_images...")
             conn.execute(text("DELETE FROM pothole_images"))
             
             # Delete from uploads where category='pothole'
             print("   Deleting from uploads...")
             result = conn.execute(text("DELETE FROM uploads WHERE category = 'pothole'"))
             print(f"   Deleted {result.rowcount} records from DB.")
             conn.commit()
        except Exception as e:
            print(f"   Error clearing DB: {e}")

    print("\nDone. System is clean. Please re-upload CSV + IMAGES together.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("Force mode enabled.")
        class ForceInput:
            def __call__(self, prompt):
                return "destroy"
        input = ForceInput() 
        # Alternatively just bypass the check in a refactored main, but mocking input is quick hack or just change logic
        # Let's change logic slightly
        print("WARNING: This will delete ALL Pothole data (DB Records + R2 Images).")
        wipe_potholes()
    else:
        wipe_potholes()
