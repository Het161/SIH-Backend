from pydantic import BaseModel
from typing import Optional, Dict, Any
import datetime

class AuditLogCreate(BaseModel):
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[Dict[Any, Any]] = None
    ip_address: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[Dict[Any, Any]]
    ip_address: Optional[str]
    timestamp: datetime.datetime
