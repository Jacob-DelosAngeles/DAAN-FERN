from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any, Union
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

class PavementSegment(BaseModel):
    points: List[List[float]] # [[lat, lon], [lat, lon]]
    type: str
    color: str

class PavementProcessResponse(BaseModel):
    success: bool
    filename: str
    count: int
    data: List[PavementSegment]

@router.get("/process/{filename}", response_model=PavementProcessResponse)
async def process_pavement_data(
    filename: str,
    current_user: UserModel = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a pavement type CSV file and return map-ready segments
    """
    # 1. Find the file in the database
    upload_record = db.query(UploadModel).filter(
        UploadModel.user_id == current_user.id,
        UploadModel.category == 'pavement',
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
        # 'type' is strict, but coordinates can vary
        if 'type' not in df.columns:
             raise ValueError("Missing 'type' column")
             
        if 'lat' in df.columns: df.rename(columns={'lat': 'latitude'}, inplace=True)
        if 'lon' in df.columns: df.rename(columns={'lon': 'longitude'}, inplace=True)
        
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
             raise ValueError("Missing latitude/longitude columns")

        # Color Map
        color_map = {
            'soil': '#8B4513',      # Brown
            'gravel': '#FFFFFF',    # White
            'flexible': '#2F2F2F',  # Dark gray
            'rigid': '#D3D3D3'      # Whitish gray (light gray)
        }
        
        segments = []
        if len(df) < 2:
            return {
                "success": True,
                "filename": filename,
                "count": 0,
                "data": []
            }
            
        current_type = None
        current_points = []
        
        # Logic to group consecutive points
        for _, row in df.iterrows():
            p_type = row['type']
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            
            # If type changes, save segment
            if current_type is not None and p_type != current_type:
                if len(current_points) >= 2:
                    segments.append({
                        "points": current_points,
                        "type": current_type,
                        "color": color_map.get(current_type, '#808080')
                    })
                current_points = []
                
            current_points.append([lat, lon])
            current_type = p_type
        
        # Add final segment
        if len(current_points) >= 2:
            segments.append({
                "points": current_points,
                "type": current_type,
                "color": color_map.get(current_type, '#808080')
            })

        return {
            "success": True,
            "filename": filename,
            "count": len(segments),
            "data": segments
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

