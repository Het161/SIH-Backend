from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.db.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogResponse
from typing import List, Optional
import datetime

router = APIRouter()

@router.get("/audit-logs")
def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = Query(50, le=500),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filters"""
    
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    # Convert UUID to string
    return [
        {
            "id": log.id,
            "user_id": str(log.user_id),
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp
        }
        for log in logs
    ]

@router.get("/audit-logs/user/{user_id}")
def get_user_audit_logs(user_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get all audit logs for a specific user"""
    
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(desc(AuditLog.timestamp)).limit(limit).all()
    
    # Convert UUID to string
    return [
        {
            "id": log.id,
            "user_id": str(log.user_id),
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp
        }
        for log in logs
    ]

@router.get("/audit-logs/task/{task_id}")
def get_task_audit_logs(task_id: str, db: Session = Depends(get_db)):
    """Get all audit logs for a specific task"""
    
    logs = db.query(AuditLog).filter(
        AuditLog.resource_type == "task",
        AuditLog.resource_id == task_id
    ).order_by(desc(AuditLog.timestamp)).all()
    
    # Convert UUID to string
    return [
        {
            "id": log.id,
            "user_id": str(log.user_id),
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp
        }
        for log in logs
    ]
