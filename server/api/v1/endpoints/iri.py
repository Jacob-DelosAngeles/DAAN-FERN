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

@router.get("/compute/{filename}")
async def compute_iri_simple(
    filename: str,
    segment_length: int = Query(default=100, description="Length of each IRI segment in meters"),
    cutoff_freq: float = Query(default=10.0, description="Cutoff frequency for filtering")
):
    """
    Compute IRI values with simple query parameters
    """
    try:
        # Check if file exists
        file_path = os.path.join("uploads", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Create request object
        request = IRIComputationRequest(
            segment_length=segment_length,
            cutoff_freq=cutoff_freq
        )
        
        # Compute IRI
        result = await iri_service.process_file_and_compute_iri(file_path, request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IRI computation failed: {str(e)}")

@router.get("/validate/{filename}")
async def validate_file(filename: str):
    """
    Validate if a file is suitable for IRI computation
    """
    try:
        file_path = os.path.join("uploads", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        is_valid, message, rows_count = await iri_service.validate_file_format(file_path)
        
        return {
            "success": True,
            "is_valid": is_valid,
            "message": message,
            "rows_count": rows_count,
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

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
