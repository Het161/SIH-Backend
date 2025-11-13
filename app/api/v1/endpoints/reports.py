# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from app.db.session import get_db
# from app.api.v1.endpoints.analytics import get_user_productivity, get_team_productivity
# from app.models.user import User
# from app.utils.reports import (
#     generate_user_productivity_pdf,
#     generate_user_productivity_excel,
#     generate_team_productivity_excel
# )
# import io

# router = APIRouter()

# @router.get("/reports/user/{user_id}/pdf")
# def export_user_report_pdf(user_id: str, db: Session = Depends(get_db)):
#     """Export user productivity report as PDF"""
    
#     user_data = get_user_productivity(user_id, db)
#     pdf_bytes = generate_user_productivity_pdf(user_data.dict())
    
#     return StreamingResponse(
#         io.BytesIO(pdf_bytes),
#         media_type="application/pdf",
#         headers={"Content-Disposition": f"attachment; filename=user_productivity_{user_id}.pdf"}
#     )

# @router.get("/reports/user/{user_id}/excel")
# def export_user_report_excel(user_id: str, db: Session = Depends(get_db)):
#     """Export user productivity report as Excel"""
    
#     user_data = get_user_productivity(user_id, db)
#     excel_bytes = generate_user_productivity_excel(user_data.dict())
    
#     return StreamingResponse(
#         io.BytesIO(excel_bytes),
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": f"attachment; filename=user_productivity_{user_id}.xlsx"}
#     )

# @router.get("/reports/team/{department}/excel")
# def export_team_report_excel(department: str, db: Session = Depends(get_db)):
#     """Export team productivity report as Excel"""
    
#     team_data = get_team_productivity(department, db)
    
#     # Get individual user data
#     users = db.query(User).filter(User.department == department).all()
#     users_data = []
#     for user in users:
#         user_stats = get_user_productivity(str(user.id), db)
#         users_data.append(user_stats.dict())
    
#     excel_bytes = generate_team_productivity_excel(team_data.dict(), users_data)
    
#     return StreamingResponse(
#         io.BytesIO(excel_bytes),
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": f"attachment; filename=team_productivity_{department}.xlsx"}
#     )

# app/api/v1/endpoints/reports.py (create this new file)

"""
Reports Email Endpoint
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

router = APIRouter(prefix="/reports", tags=["reports"])
logger = logging.getLogger(__name__)


class EmailReportRequest(BaseModel):
    recipient_email: EmailStr
    report_type: str
    subject: str
    message: str = ""


def send_email_report(recipient: str, subject: str, body: str, attachment_data: str = None):
    """Send email with optional attachment"""
    try:
        # Email configuration (use environment variables in production!)
        SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
        SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'html'))
        
        # Add attachment if provided
        if attachment_data:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data.encode())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename=report.pdf')
            msg.attach(part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@router.post("/email")
async def email_report(
    request: EmailReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send report via email
    """
    try:
        # Generate email body
        email_body = f"""
        <html>
        <body>
            <h2>SmartWork 360 Report</h2>
            <p><strong>Report Type:</strong> {request.report_type}</p>
            <p><strong>Generated by:</strong> {current_user.full_name}</p>
            <p><strong>Email:</strong> {current_user.email}</p>
            <hr>
            <p>{request.message if request.message else 'Please find the attached report.'}</p>
            <br>
            <p>Best regards,<br>SmartWork 360 Team</p>
        </body>
        </html>
        """
        
        # Send email in background
        background_tasks.add_task(
            send_email_report,
            recipient=request.recipient_email,
            subject=request.subject,
            body=email_body
        )
        
        return {
            "success": True,
            "message": f"Email will be sent to {request.recipient_email}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send report: {str(e)}"
        )

