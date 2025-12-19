from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import pandas as pd
import os
from pathlib import Path
import math
from core.config import settings
from utils.file_handler import FileHandler

from models.upload import UploadModel
from models.user import UserModel
from core.database import get_db
from core import security
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

router = APIRouter()
file_handler = FileHandler()

@router.get("/process/{filename}", response_model=Dict[str, Any])
async def process_pothole_data(
    filename: str,
    current_user: UserModel = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process an uploaded pothole detection CSV file.
    Returns a list of pothole markers with popup HTML.
    """
    # 1. Try to find the file in the database for the current user
    upload_record = db.query(UploadModel).filter(
        UploadModel.user_id == current_user.id,
        (UploadModel.category == 'pothole'), 
        (UploadModel.file_type == 'csv'),
        (UploadModel.filename == filename) | (UploadModel.original_filename == filename)
    ).order_by(UploadModel.upload_date.desc()).first()

    if not upload_record:
         # Fallback to legacy check if no record found (though for fresh DB this matters less)
         # We might want to construct a path or search? 
         # Given the error is "File not found: pothole_detections.csv", the user likely uploaded it via the UI
         # and it should have a record.
         pass
    
    try:
        if upload_record:
             # Use the storage path from the record
             path_to_read = upload_record.storage_path
        else:
             # Fallback attempt if we can guess the path or if filename is the path (legacy)
             # But with R2, filename isn't enough without directory structure.
             raise HTTPException(status_code=404, detail=f"File record not found for: {filename}")

        # Get content using storage service (works for Local and R2)
        content_bytes = file_handler.storage.get_file_content(path_to_read)
        
        from io import BytesIO
        df = pd.read_csv(BytesIO(content_bytes))
        
        # Validate columns
        required_columns = ['latitude', 'longitude', 'image_path', 'confidence_score']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing_cols}")
        
        # 2. Fetch all pothole image records for this user to create a filename -> storage_path map
        # This is necessary because files in R2 are renamed to UUIDs, but the CSV contains original filenames.
        image_records = db.query(UploadModel).filter(
            UploadModel.user_id == current_user.id,
            UploadModel.category == 'pothole',
            UploadModel.file_type.in_(['jpg', 'jpeg', 'png']) 
        ).all()
        
        # Create lookup dictionary: original_filename -> storage_path
        # Use simple filename (basename) for matching just in case
        image_map = {rec.original_filename: rec.storage_path for rec in image_records}
        
        markers_data = []
        
        for idx, row in df.iterrows():
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                
                if math.isnan(lat) or math.isnan(lon):
                    continue
                    
                image_path = row['image_path'] # e.g. "frame_11030.jpg"
                confidence = float(row['confidence_score'])
                
                # Resolve R2 URL
                # Check if we have a mapped storage path for this filename
                if image_path in image_map:
                    storage_key = image_map[image_path]
                    image_url = f"{settings.R2_PUBLIC_URL}/{storage_key}"
                else:
                    # Fallback: maybe it wasn't renamed or missing? 
                    # Try constructing it assuming standard renamed path if we can (impossible with random UUID)
                    # For now, default to the constructed guess, but it likely 404s
                    # Or check if image_path already looks like a path?
                    full_image_key = f"{current_user.id}/pothole/{image_path}"
                    image_url = f"{settings.R2_PUBLIC_URL}/{full_image_key}"
                
                # Create popup HTML (mirrored from streamlit_app.py)
                popup_html = f"""
                <div style="text-align: center; min-width: 250px; font-family: Arial, sans-serif;">
                    <h4 style="margin: 0 0 10px 0; color: #2c3e50;">🚧 Pothole Detection</h4>
                    <p style="margin: 5px 0;"><strong>Confidence:</strong> {confidence:.2%}</p>
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">{image_path}</p>
                    
                    <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
                        <a href="{image_url}" target="_blank">
                            <img src="{image_url}" 
                                 style="width: 200px; height: auto; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer;" 
                                 onerror="this.style.display='none'; this.parentElement.nextElementSibling.style.display='block';"
                                 alt="Pothole Detection Image">
                        </a>
                        <div style="display: none; color: #e74c3c; font-size: 12px; padding: 10px;">
                            ❌ Image failed to load<br>
                            <a href="{image_url}" target="_blank" style="color: #007bff; text-decoration: none; font-size: 10px;">Click here to view image</a>
                        </div>
                    </div>
                    
                    <p style="margin: 5px 0; font-size: 10px; color: #999;">
                        <a href="{image_url}" target="_blank" style="color: #007bff; text-decoration: none;">View full image in new tab</a>
                    </p>
                </div>
                """
                
                markers_data.append({
                    'lat': lat,
                    'lon': lon,
                    'popup_html': popup_html,
                    'tooltip': f"Pothole Detection ({confidence:.1%})",
                    'confidence': confidence,
                    'image_path': image_path,
                    'image_url': image_url,
                    'id': idx
                })
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
                
        return {
            "success": True,
            "data": markers_data,
            "count": len(markers_data)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
