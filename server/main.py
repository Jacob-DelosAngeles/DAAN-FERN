import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verify the IRI calculator can be imported
try:
    from iri_calculator import IRICalculator
    logger.info("IRI Calculator imported successfully")
except ImportError as e:
    logger.error(f"Failed to import IRI Calculator: {e}")
    exit(1)

from api.v1.endpoints import auth, upload, iri, pothole, vehicle, pavement
from core.config import settings
from core.database import engine
from models import user, upload as upload_models

# Create database tables
user.Base.metadata.create_all(bind=engine)
upload_models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Digital Analytics for Asset-based Navigation of Roads",
    version=settings.PROJECT_VERSION
)

# Configure CORS from environment variable (comma-separated list)
# Example: CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
cors_origins_str = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
)
origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

logger.info(f"CORS allowed origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["upload"])
app.include_router(iri.router, prefix=f"{settings.API_V1_STR}/iri", tags=["iri"])
app.include_router(pothole.router, prefix=f"{settings.API_V1_STR}/pothole", tags=["pothole"])
app.include_router(vehicle.router, prefix=f"{settings.API_V1_STR}/vehicle", tags=["vehicle"])
app.include_router(pavement.router, prefix=f"{settings.API_V1_STR}/pavement", tags=["pavement"])

@app.get("/")
async def root():
    return {"message": "Project DAAN Express API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Project DAAN Express API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
