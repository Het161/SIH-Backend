from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List
import os

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL_USERNAME", "your-email@gmail.com"),
    MAIL_PASSWORD=os.getenv("EMAIL_PASSWORD", "your-app-password"),
    MAIL_FROM=os.getenv("EMAIL_FROM", "your-email@gmail.com"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="SIH Productivity Tracker",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

async def send_task_notification(recipient: str, task_title: str, due_date: str):
    """Send email when task is assigned"""
    html = f"""
    <h2>New Task Assigned!</h2>
    <p><strong>Task:</strong> {task_title}</p>
    <p><strong>Due Date:</strong> {due_date}</p>
    <p>Please login to view details.</p>
    """
    
    message = MessageSchema(
        subject="New Task Assigned - Government Productivity Tracker",
        recipients=[recipient],
        body=html,
        subtype="html"
    )
    
    await fm.send_message(message)
