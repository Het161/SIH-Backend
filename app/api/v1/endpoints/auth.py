from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.db.session import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse
from app.services.email_service import send_welcome_email

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,  # Keep this for now
    db: Session = Depends(get_db)
):
    """Register a new user and send welcome email"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        department=user_data.department
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"✅ User registered: {new_user.email}")
    
    # ✅ SEND EMAIL IMMEDIATELY (await instead of background_tasks)
    try:
        logger.info(f"📧 Attempting to send welcome email to: {new_user.email}")
        
        result = await send_welcome_email(
            user_email=new_user.email,
            user_name=new_user.full_name,
            user_role=new_user.role,
            user_department=new_user.department or "Not specified"
        )
        
        if result:
            logger.info(f"✅ Welcome email sent successfully to: {new_user.email}")
        else:
            logger.error(f"❌ Failed to send welcome email to: {new_user.email}")
            
    except Exception as e:
        logger.error(f"❌ Error sending welcome email: {str(e)}")
        # Don't fail registration if email fails
    
    return new_user


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )
    
    # Create access token
    access_token = create_access_token({
        "sub": user.email,
        "user_id": user.id,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
    })
    
    # Return token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "department": user.department,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    }


@router.get("/me")
async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    from app.core.security import decode_access_token
    
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "department": user.department,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )






