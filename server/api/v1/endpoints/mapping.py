from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import os
import shutil
from services.mapping_service import MappingService
from models.mapping_models import VehicleMappingResponse, PotholeMappingResponse, PavementMappingResponse
from utils.file_handler import FileHandler

router = APIRouter()
mapping_service = MappingService()
file_handler = FileHandler()

@router.post("/vehicle", response_model=VehicleMappingResponse)
async def map_vehicles(files: List[UploadFile] = File(...)):
    """
    Upload vehicle detection CSVs and get mapping data
    """
    saved_paths = []
    try:
        for file in files:
            path = await file_handler.save_uploaded_file(file)
            saved_paths.append(path)
            
        markers, count = mapping_service.process_vehicle_data(saved_paths)
        
        return VehicleMappingResponse(
            success=True,
            message=f"Processed {count} vehicle markers",
            data=markers,
            total_items=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        for path in saved_paths:
            file_handler.cleanup_file(path)

@router.post("/pothole", response_model=PotholeMappingResponse)
async def map_potholes(files: List[UploadFile] = File(...)):
    """
    Upload pothole detection CSVs and get mapping data
    """
    saved_paths = []
    try:
        for file in files:
            path = await file_handler.save_uploaded_file(file)
            saved_paths.append(path)
            
        markers, count = mapping_service.process_pothole_data(saved_paths)
        
        return PotholeMappingResponse(
            success=True,
            message=f"Processed {count} pothole markers",
            data=markers,
            total_items=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in saved_paths:
            file_handler.cleanup_file(path)

@router.post("/pavement", response_model=PavementMappingResponse)
async def map_pavement(files: List[UploadFile] = File(...)):
    """
    Upload pavement type CSVs and get mapping data
    """
    saved_paths = []
    try:
        for file in files:
            path = await file_handler.save_uploaded_file(file)
            saved_paths.append(path)
            
        segments, count = mapping_service.process_pavement_data(saved_paths)
        
        return PavementMappingResponse(
            success=True,
            message=f"Processed {count} pavement segments",
            data=segments,
            total_items=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in saved_paths:
            file_handler.cleanup_file(path)
