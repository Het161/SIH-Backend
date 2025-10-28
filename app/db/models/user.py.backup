from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.session import Base


class User(Base):
    """User model for employees (Admin, Manager, Employee roles)"""
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User Information
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Role-based access control
    role = Column(
        SQLEnum('admin', 'manager', 'employee', name='user_roles'),
        nullable=False,
        default='employee'
    )
    
    # Department/Office hierarchy
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    office_location = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(SQLEnum('active', 'inactive', name='user_status'), default='active')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (will be used later)
    # tasks_assigned = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    # tasks_created = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    
    def __repr__(self):
        return f"<User {self.name} ({self.role})>"
