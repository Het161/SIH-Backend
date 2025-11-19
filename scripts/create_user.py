"""
Create a test user for SmartWork 360
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models import User
from app.core.security import get_password_hash


def create_test_user():
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == "kathanp526@gmail.com").first()
        
        if existing_user:
            print(f"✅ User already exists: {existing_user.email}")
            print(f"   Full Name: {existing_user.full_name}")
            print(f"   Role: {existing_user.role}")
            print(f"   Is Active: {existing_user.is_active}")
            
            # Update password
            new_password = "Admin@123"
            existing_user.hashed_password = get_password_hash(new_password)
            db.commit()
            print(f"✅ Password updated to: {new_password}")
        else:
            # Create new user
            new_user = User(
                email="kathanp526@gmail.com",
                full_name="Kathan Patel",
                hashed_password=get_password_hash("Admin@123"),
                role="admin",
                department="IT",
                is_active=True,
                is_superuser=True,
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print("✅ Test user created successfully!")
            print(f"   Email: {new_user.email}")
            print(f"   Password: Admin@123")
            print(f"   Role: {new_user.role}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()  