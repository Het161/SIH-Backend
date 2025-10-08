from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    Token
)
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token
)

# Create router - THIS LINE IS CRITICAL!
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        department=user_data.department,
        designation=user_data.designation,
        office_location=user_data.office_location,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """Login and get access token"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if user.is_active != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated",
        )
    
    # Create token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
