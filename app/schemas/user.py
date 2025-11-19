# from pydantic import BaseModel, EmailStr, Field
# from datetime import datetime
# from typing import Optional


# class UserBase(BaseModel):
#     email: EmailStr
#     full_name: str = Field(..., min_length=2, max_length=100)
#     role: str = Field(..., pattern="^(admin|manager|employee)$")
#     department: Optional[str] = None
#     designation: Optional[str] = None
#     office_location: Optional[str] = None


# class UserCreate(UserBase):
#     password: str = Field(..., min_length=8, max_length=50)


# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str


# class UserUpdate(BaseModel):
#     full_name: Optional[str] = Field(None, min_length=2, max_length=100)
#     department: Optional[str] = None
#     designation: Optional[str] = None
#     office_location: Optional[str] = None


# class UserResponse(UserBase):
#     id: int
#     is_active: bool
#     created_at: datetime

#     model_config = {
#         "from_attributes": True,  # Use 'from_attributes' instead of 'orm_mode'
#     }


# class Token(BaseModel):
#     access_token: str
#     token_type: str = "bearer"
#     user: UserResponse


# class TokenData(BaseModel):
#     user_id: Optional[str] = None
#     role: Optional[str] = None



from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    designation: Optional[str] = None
    office_location: Optional[str] = None


# ============================================================================
# CREATE/REGISTER SCHEMA
# ============================================================================

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    department: str = Field(..., min_length=2, max_length=100)
    role: str  # ✅ Accept as string from frontend
    designation: Optional[str] = None
    office_location: Optional[str] = None
    
    @validator('role')
    def validate_role(cls, v):
        """Validate and normalize role to lowercase"""
        if v.lower() not in ['user', 'admin']:
            raise ValueError('Role must be either "user" or "admin"')
        return v.lower()  # ✅ Return lowercase string
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    model_config = {
        "from_attributes": True,
    }


# ============================================================================
# LOGIN SCHEMA
# ============================================================================

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


# ============================================================================
# UPDATE SCHEMA
# ============================================================================

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    designation: Optional[str] = None
    office_location: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
    }


# ============================================================================
# RESPONSE SCHEMA
# ============================================================================

class UserResponse(BaseModel):
    """Schema for user response (returned after registration/login)"""
    id: int
    email: str
    full_name: str
    role: str  # ✅ Return as string
    department: str
    designation: Optional[str] = None
    office_location: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
    }


# ============================================================================
# TOKEN SCHEMAS
# ============================================================================

class Token(BaseModel):
    """Schema for access token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for decoded token data"""
    user_id: Optional[str] = None
    role: Optional[str] = None




