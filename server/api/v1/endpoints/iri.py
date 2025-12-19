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
    Compute IRI values for an uploaded file
    """
    try:
        # 1. Try to find the file in the database for the current user
        upload_record = db.query(UploadModel).filter(
            UploadModel.user_id == current_user.id,
            (UploadModel.file_type == 'csv'), # Optimization
            (UploadModel.filename == filename) | (UploadModel.original_filename == filename)
        ).order_by(UploadModel.upload_date.desc()).first()

        if upload_record:
             # Use storage path from DB
             # If we have a record, we trust this path. If it fails, we want to know why (500), not hide it as 404.
             storage_path = upload_record.storage_path
             content_bytes = file_handler.storage.get_file_content(storage_path)
        else:
             # Fallback: assume filename is the path or try to construct it
             storage_path = filename
             try:
                 content_bytes = file_handler.storage.get_file_content(storage_path)
             except Exception:
                 # Try constructing path if first attempt failed and it's R2 (user_id/iri/filename)
                 try:
                     alt_path = f"{current_user.id}/iri/{filename}"
                     content_bytes = file_handler.storage.get_file_content(alt_path)
                 except Exception:
                     # Raise 404 if truly not found
                     raise HTTPException(status_code=404, detail=f"File not found in storage: {filename}")

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

