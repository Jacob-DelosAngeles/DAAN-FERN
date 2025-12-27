from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid
import hashlib
from datetime import datetime
import logging

from models.user import UserModel
from models.upload import UploadModel, PotholeImageModel
from core.database import get_db
from core.clerk_auth import get_current_user
from services.storage_service import get_storage_service, R2StorageService

logger = logging.getLogger(__name__)

router = APIRouter()

# Get storage service
storage = get_storage_service()


class PresignRequest(BaseModel):
    """Request for a presigned upload URL"""
    filename: str
    content_type: str = "image/jpeg"
    category: str = "pothole"


class PresignResponse(BaseModel):
    """Response with presigned URL"""
    upload_url: str
    object_key: str
    filename: str


class RegisterUploadRequest(BaseModel):
    """Register a file that was uploaded directly to R2"""
    object_key: str
    original_filename: str
    file_size: int
    content_type: str
    category: str = "pothole"
    file_hash: Optional[str] = None


class RegisterUploadResponse(BaseModel):
    """Response after registering upload"""
    success: bool
    id: int
    message: str


class BatchPresignRequest(BaseModel):
    """Request presigned URLs for multiple files"""
    files: List[PresignRequest]


class BatchPresignResponse(BaseModel):
    """Response with multiple presigned URLs"""
    urls: List[PresignResponse]


@router.post("/upload", response_model=PresignResponse)
async def get_presigned_upload_url(
    request: PresignRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a presigned URL for direct browser-to-R2 upload.
    The URL is valid for 5 minutes.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can upload files")
    
    if not isinstance(storage, R2StorageService):
        raise HTTPException(
            status_code=501, 
            detail="Direct upload only supported with R2 storage"
        )
    
    try:
        # Generate unique object key
        file_ext = request.filename.split('.')[-1].lower() if '.' in request.filename else 'jpg'
        unique_id = str(uuid.uuid4())
        object_key = f"{current_user.id}/{request.category}/{unique_id}.{file_ext}"
        
        # Generate presigned URL
        upload_url = storage.generate_presigned_upload_url(
            object_key=object_key,
            content_type=request.content_type,
            expires_in=300  # 5 minutes
        )
        
        return PresignResponse(
            upload_url=upload_url,
            object_key=object_key,
            filename=request.filename
        )
        
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/batch", response_model=BatchPresignResponse)
async def get_batch_presigned_urls(
    request: BatchPresignRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get presigned URLs for multiple files at once.
    More efficient than requesting one at a time.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can upload files")
    
    if not isinstance(storage, R2StorageService):
        raise HTTPException(
            status_code=501, 
            detail="Direct upload only supported with R2 storage"
        )
    
    urls = []
    for file_req in request.files:
        try:
            file_ext = file_req.filename.split('.')[-1].lower() if '.' in file_req.filename else 'jpg'
            unique_id = str(uuid.uuid4())
            object_key = f"{current_user.id}/{file_req.category}/{unique_id}.{file_ext}"
            
            upload_url = storage.generate_presigned_upload_url(
                object_key=object_key,
                content_type=file_req.content_type,
                expires_in=300
            )
            
            urls.append(PresignResponse(
                upload_url=upload_url,
                object_key=object_key,
                filename=file_req.filename
            ))
        except Exception as e:
            logger.warning(f"Failed to generate URL for {file_req.filename}: {e}")
            # Continue with other files
    
    return BatchPresignResponse(urls=urls)


@router.post("/register", response_model=RegisterUploadResponse)
async def register_upload(
    request: RegisterUploadRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a file that was uploaded directly to R2.
    This creates the database record after the direct upload completes.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can upload files")
    
    try:
        # Get file extension
        file_ext = request.original_filename.split('.')[-1].lower() if '.' in request.original_filename else ''
        
        # Create upload record
        db_upload = UploadModel(
            user_id=current_user.id,
            filename=request.object_key.split('/')[-1],  # UUID filename
            original_filename=request.original_filename,
            file_type=file_ext,
            category=request.category,
            storage_path=request.object_key,
            file_size=request.file_size,
            file_hash=request.file_hash or hashlib.md5(request.object_key.encode()).hexdigest()
        )
        db.add(db_upload)
        db.commit()
        db.refresh(db_upload)
        
        # For pothole images, link to most recent CSV
        if request.category == "pothole" and file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            # Find the most recent pothole CSV for this user
            csv_upload = db.query(UploadModel).filter(
                UploadModel.user_id == current_user.id,
                UploadModel.category == 'pothole',
                UploadModel.file_type == 'csv'
            ).order_by(UploadModel.upload_date.desc()).first()
            
            if csv_upload:
                pothole_image = PotholeImageModel(
                    upload_id=csv_upload.id,
                    image_path=request.object_key
                )
                db.add(pothole_image)
                db.commit()
        
        logger.info(f"Registered direct upload: {request.original_filename} -> {request.object_key}")
        
        return RegisterUploadResponse(
            success=True,
            id=db_upload.id,
            message=f"Registered {request.original_filename}"
        )
        
    except Exception as e:
        logger.error(f"Failed to register upload: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
