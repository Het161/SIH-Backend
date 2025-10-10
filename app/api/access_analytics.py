from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models.access_log import APIAccessLog
from typing import List
from pydantic import BaseModel


router = APIRouter(prefix="/api/analytics", tags=["Access Analytics"])


class AccessUsageResponse(BaseModel):
    role: str
    path: str
    count: int


@router.get("/access-usage", response_model=List[AccessUsageResponse])
def access_usage(db: Session = Depends(get_db)):
    """Get API access statistics grouped by role and path"""
    results = (
        db.query(
            APIAccessLog.user_role,
            APIAccessLog.path,
            func.count(APIAccessLog.id).label("count")
        )
        .group_by(APIAccessLog.user_role, APIAccessLog.path)
        .all()
    )
    
    return [
        {"role": r.user_role, "path": r.path, "count": r.count}
        for r in results
    ]


@router.get("/access-by-role/{role}")
def access_by_role(role: str, db: Session = Depends(get_db)):
    """Get all access logs for a specific role"""
    logs = db.query(APIAccessLog).filter(APIAccessLog.user_role == role).all()
    return {"role": role, "total_requests": len(logs), "logs": logs}
