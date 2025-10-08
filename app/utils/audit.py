from sqlalchemy.orm import Session
from app.db.models.audit_log import AuditLog
from typing import Optional, Dict, Any

def log_action(
    db: Session,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[Any, Any]] = None,
    ip_address: Optional[str] = None
):
    """Helper function to create audit log entries"""
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )
    db.add(audit_log)
    db.commit()
    return audit_log
