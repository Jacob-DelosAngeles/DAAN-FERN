from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
import os
import pandas as pd
from sqlalchemy.orm import Session
from pydantic import BaseModel
from io import BytesIO

from models.upload import UploadModel
from models.user import UserModel
from core.database import get_db
from core import security
from core.config import settings
from utils.file_handler import FileHandler

router = APIRouter()
file_handler = FileHandler()

class VehicleDetection(BaseModel):
    lat: float
    lon: float
    type: str
    count: int = 1

class VehicleProcessResponse(BaseModel):
    success: bool
    filename: str
    count: int
    data: List[VehicleDetection]

@router.get("/process/{filename}", response_model=VehicleProcessResponse)
async def process_vehicle_data(
    filename: str,
    current_user: UserModel = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a vehicle detection CSV file and return map-ready data.
    - Admins: Can only process their own files
    - Users: Can process ANY file (shared read-only access)
    """
    # Find the file in the database
    if current_user.is_admin:
        # Admins see only their own files
        upload_record = db.query(UploadModel).filter(
            UploadModel.user_id == current_user.id,
            UploadModel.category == 'vehicle',
            UploadModel.file_type == 'csv',
            (UploadModel.filename == filename) | (UploadModel.original_filename == filename)
        ).order_by(UploadModel.upload_date.desc()).first()
    else:
        # Regular users can see ANY file (shared data)
        upload_record = db.query(UploadModel).filter(
            UploadModel.category == 'vehicle',
            UploadModel.file_type == 'csv',
            (UploadModel.filename == filename) | (UploadModel.original_filename == filename)
        ).order_by(UploadModel.upload_date.desc()).first()

    if not upload_record:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    try:
        # 2. Get file content from storage (works for both local and R2)
        content_bytes = file_handler.storage.get_file_content(upload_record.storage_path)
        df = pd.read_csv(BytesIO(content_bytes))
        
        # Normalize column names
        df.columns = [c.lower() for c in df.columns]
        
        # Check required columns
        required = ['latitude', 'longitude', 'vehicle_type']
        missing = [c for c in required if c not in df.columns]
        if missing:
            # Try fallback names if specific ones missing
            if 'lat' in df.columns: df.rename(columns={'lat': 'latitude'}, inplace=True)
            if 'lon' in df.columns: df.rename(columns={'lon': 'longitude'}, inplace=True)
            
            # Recheck
            missing = [c for c in required if c not in df.columns]
            if missing:
                raise ValueError(f"Missing columns: {missing}")

        # Filter rows
        valid_types = ['car', 'truck', 'bicycle', 'motorcycle']
        df = df[df['vehicle_type'].isin(valid_types)].copy()
        
        if df.empty:
            return {
                "success": True,
                "filename": filename,
                "count": 0,
                "data": []
            }
        
        # Convert to list of objects
        result_data = []
        for _, row in df.iterrows():
            result_data.append({
                "lat": float(row['latitude']),
                "lon": float(row['longitude']),
                "type": row['vehicle_type'],
                "count": 1
            })
            
        return {
            "success": True,
            "filename": filename,
            "count": len(result_data),
            "data": result_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

