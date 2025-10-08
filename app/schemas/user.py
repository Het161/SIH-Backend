from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., pattern="^(admin|manager|employee)$")
    department: Optional[str] = None
    designation: Optional[str] = None
    office_location: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating new user (includes password)"""
    password: str = Field(..., min_length=8, max_length=50)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user details"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    department: Optional[str] = None
    designation: Optional[str] = None
    office_location: Optional[str] = None


class UserResponse(UserBase):
    """Schema for returning user data (no password)"""
    id: UUID
    is_active: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows SQLAlchemy models to be converted


class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for decoded token data"""
    user_id: Optional[str] = None
    role: Optional[str] = None
