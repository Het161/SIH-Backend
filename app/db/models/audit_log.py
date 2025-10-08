import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(50))  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(50))  # task, user, review, etc.
    resource_id = Column(String(100))  # ID of the resource
    details = Column(JSONB)  # Additional context as JSON
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
