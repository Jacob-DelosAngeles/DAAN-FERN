from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import os
from io import BytesIO

from models.iri_models import IRIComputationRequest, IRIComputationResponse, ErrorResponse
from models.upload import UploadModel
from models.user import UserModel
from services.iri_service import IRIService
from core.database import get_db
from core import security
from core.config import settings 
from sqlalchemy.orm import Session
from fastapi import Depends
from utils.file_handler import FileHandler

router = APIRouter()

# Initialize service
iri_service = IRIService()
file_handler = FileHandler()

@router.post("/compute/{filename}", response_model=IRIComputationResponse)
async def compute_iri(
    filename: str,
    request: IRIComputationRequest = IRIComputationRequest(),
    current_user: UserModel = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compute IRI values for an uploaded file.
    - All users can view shared data (read-only for non-admins)
    """
    try:
        # 1. Find the file in the database - ALL users see shared data
        upload_record = db.query(UploadModel).filter(
            UploadModel.file_type == 'csv',
            (UploadModel.filename == filename) | (UploadModel.original_filename == filename)
        ).order_by(UploadModel.upload_date.desc()).first()

        if not upload_record:
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # Use storage path from DB record
        storage_path = upload_record.storage_path
        content_bytes = file_handler.storage.get_file_content(storage_path)

        file_obj = BytesIO(content_bytes)
        
        # Compute IRI
        # process_file_and_compute_iri now needs to accept a file-like object
        # We verified IRICalculator.load_data uses pd.read_csv which accepts file objects.
        # However, iri_service.process_file_and_compute_iri signature calls for file_path: str
        # but Python is dynamic. Let's hope it passes it through to load_data.
        # Check iri_service.py: it calls self.calculator.load_data(file_path).
        # So passing file_obj should work!
        result = await iri_service.process_file_and_compute_iri(file_obj, request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IRI computation failed: {str(e)}")


@router.get("/cached/{filename}")
async def get_cached_iri(
    filename: str,
    current_user: UserModel = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pre-processed IRI data from cache (INSTANT - no processing).
    This is the preferred endpoint for fetching IRI data.
    Data is cached during upload for fast retrieval.
    """
    import json
    
    # Find the file record (shared data model - all users can see)
    upload_record = db.query(UploadModel).filter(
        UploadModel.file_type == 'csv',
        (UploadModel.filename == filename) | (UploadModel.original_filename == filename)
    ).order_by(UploadModel.upload_date.desc()).first()
    
    if not upload_record:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    # Return cached data if available
    if upload_record.cached_data:
        try:
            cached = json.loads(upload_record.cached_data)
            cached['from_cache'] = True
            return cached
        except json.JSONDecodeError:
            pass  # Fall through to processing
    
    # No cache available - return error (upload should have cached it)
    raise HTTPException(
        status_code=404, 
        detail="IRI data not cached. Please re-upload the file."
    )


# NOTE: Legacy GET /compute/{filename} and GET /validate/{filename} endpoints
# have been removed because they:
# 1. Did not require authentication
# 2. Only worked with local storage (not R2)
# Use the POST /compute/{filename} endpoint instead, which requires authentication.

@router.get("/status")
async def get_service_status():
    """
    Get the current status of the IRI computation service
    """
    return {
        "success": True,
        "service": "IRI Computation Service",
        "status": "running",
        "version": "1.0.0"
    }

