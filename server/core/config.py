import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Project DAAN Express API"
    PROJECT_VERSION: str = "1.0.0"
    
    # SECURITY: SECRET_KEY must be set via environment variable
    # Generate with: openssl rand -hex 32
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Increased from 30
    
    def __init__(self):
        # Validate required settings
        if not self.SECRET_KEY:
            # Allow missing key in dev mode only
            import warnings
            warnings.warn("SECRET_KEY not set! Using insecure default for development only.")
            self.SECRET_KEY = "dev-only-insecure-key-change-in-production"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_PUBLISHABLE_KEY: str = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    
    # Storage
    STORAGE_MODE: str = os.getenv("STORAGE_MODE", "local")  # local, s3
    R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
    R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
    R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "daan-bucket")
    R2_ENDPOINT_URL: str = os.getenv("R2_ENDPOINT_URL", "")
    R2_PUBLIC_URL: str = os.getenv("R2_PUBLIC_URL", "")  # Required in production
    
    API_V1_STR: str = "/api/v1"
    
    # Server configuration
    # Required for generating absolute proxy URLs (e.g. from Vercel to Render)
    # Example: https://my-backend.onrender.com
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

settings = Settings()
