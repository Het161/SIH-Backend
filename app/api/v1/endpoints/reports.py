from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.endpoints.analytics import get_user_productivity, get_team_productivity
from app.db.models.user import User
from app.utils.reports import (
    generate_user_productivity_pdf,
    generate_user_productivity_excel,
    generate_team_productivity_excel
)
import io

router = APIRouter()

@router.get("/reports/user/{user_id}/pdf")
def export_user_report_pdf(user_id: str, db: Session = Depends(get_db)):
    """Export user productivity report as PDF"""
    
    user_data = get_user_productivity(user_id, db)
    pdf_bytes = generate_user_productivity_pdf(user_data.dict())
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=user_productivity_{user_id}.pdf"}
    )

@router.get("/reports/user/{user_id}/excel")
def export_user_report_excel(user_id: str, db: Session = Depends(get_db)):
    """Export user productivity report as Excel"""
    
    user_data = get_user_productivity(user_id, db)
    excel_bytes = generate_user_productivity_excel(user_data.dict())
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=user_productivity_{user_id}.xlsx"}
    )

@router.get("/reports/team/{department}/excel")
def export_team_report_excel(department: str, db: Session = Depends(get_db)):
    """Export team productivity report as Excel"""
    
    team_data = get_team_productivity(department, db)
    
    # Get individual user data
    users = db.query(User).filter(User.department == department).all()
    users_data = []
    for user in users:
        user_stats = get_user_productivity(str(user.id), db)
        users_data.append(user_stats.dict())
    
    excel_bytes = generate_team_productivity_excel(team_data.dict(), users_data)
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=team_productivity_{department}.xlsx"}
    )
