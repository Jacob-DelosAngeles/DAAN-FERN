from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

# Valid roles in the system
VALID_ROLES = ["superuser", "admin", "user"]

# SQLAlchemy Model
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    clerk_id = Column(String, unique=True, index=True, nullable=True)  # Clerk user ID
    full_name = Column(String, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)  # Nullable for Clerk-only users
    is_active = Column(Boolean, default=True)
    # Role field: "superuser" (owner), "admin" (can upload), "user" (read-only)
    role = Column(String, default="user")
    
    # Backwards compatibility property
    @property
    def is_superuser(self) -> bool:
        return self.role == "superuser"
    
    @property
    def is_admin(self) -> bool:
        return self.role in ["superuser", "admin"]
    
    # Relationships
    uploads = relationship("UploadModel", back_populates="user", cascade="all, delete-orphan")

# Pydantic Schemas
class UserBase(BaseModel):
    email: str  # Changed from EmailStr to support Clerk synthetic emails
    full_name: Optional[str] = None
    is_active: bool = True
    role: str = "user"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    # Computed field for backwards compatibility
    @property
    def is_superuser(self) -> bool:
        return self.role == "superuser"
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
