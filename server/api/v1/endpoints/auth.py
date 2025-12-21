from datetime import timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, InterfaceError
import time
import logging

from core import security
from core.config import settings
from core.database import get_db
from models.user import Token, User, UserCreate, UserModel, VALID_ROLES
from jose import jwt, JWTError

router = APIRouter()
logger = logging.getLogger(__name__)


def db_query_with_retry(db: Session, query_func, max_retries: int = 3):
    """Execute a database query with retry logic for connection failures."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return query_func()
        except (OperationalError, InterfaceError) as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 0.5 * (2 ** attempt)  # Exponential backoff
                logger.warning(f"DB connection retry {attempt + 1}/{max_retries} in {wait_time}s...")
                time.sleep(wait_time)
                # Try to reconnect
                try:
                    db.rollback()
                except:
                    pass
            continue
    
    raise last_error


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Use retry logic for the database query
    try:
        user = db_query_with_retry(
            db,
            lambda: db.query(UserModel).filter(UserModel.email == form_data.username).first()
        )
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection failed during login: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable. Please try again."
        )
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, role=user.role, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=User)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new user without the need to be logged in.
    Note: New users are always registered as regular users for security.
    """
    # Check if user exists with retry
    try:
        user = db_query_with_retry(
            db,
            lambda: db.query(UserModel).filter(UserModel.email == user_in.email).first()
        )
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection failed during registration check: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable. Please try again."
        )
    
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    hashed_password = security.get_password_hash(user_in.password)
    db_user = UserModel(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_active=True,
        role="user",  # SECURITY: New users always start as regular users
    )
    
    # Save with retry
    try:
        def save_user():
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        
        return db_query_with_retry(db, save_user)
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Database connection failed during registration save: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable. Please try again."
        )

@router.get("/users", response_model=List[User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: UserModel = Depends(security.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve all users (Superuser only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not authorized. Superuser access required."
        )
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}/role", response_model=User)
def update_user_role(
    user_id: int,
    role: str,
    current_user: UserModel = Depends(security.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update user role (Superuser only).
    Roles: 'admin' (can upload/manage data), 'user' (read-only).
    Note: Only superusers can promote users to admin or demote admins to user.
    Superuser role cannot be assigned via this endpoint.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, 
            detail="Only superusers can manage user roles."
        )
    
    # Validate role value
    if role not in ["admin", "user"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role. Allowed roles: admin, user"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    
    # Prevent superusers from being demoted (including self)
    if user.role == "superuser":
        raise HTTPException(
            status_code=400,
            detail="Cannot change the role of a superuser."
        )
    
    user.role = role
    db.commit()
    db.refresh(user)
    return user
