from fastapi import APIRouter, BackgroundTasks
from pydantic import EmailStr
import asyncio

router = APIRouter(prefix="/api/notifications", tags=["Email Notifications"])

async def mock_send_email(recipient: str, subject: str, content: str):
    """Mock email sending for demo - logs instead of actually sending"""
    await asyncio.sleep(0.5)  # Simulate sending delay
    print(f"📧 EMAIL SENT TO: {recipient}")
    print(f"📌 SUBJECT: {subject}")
    print(f"📄 CONTENT: {content[:100]}...")
    return True

@router.post("/send-task-email")
async def send_task_notification(
    recipient_email: EmailStr,
    task_title: str,
    task_description: str,
    due_date: str,
    background_tasks: BackgroundTasks
):
    """Send email notification when task is assigned (DEMO MODE)"""
    
    html_content = f"""
    <h2>🎯 New Task Assigned!</h2>
    <p><strong>Task:</strong> {task_title}</p>
    <p><strong>Description:</strong> {task_description}</p>
    <p><strong>Due Date:</strong> {due_date}</p>
    """
    
    background_tasks.add_task(
        mock_send_email,
        recipient_email,
        f"📋 New Task: {task_title}",
        html_content
    )
    
    return {
        "message": "✅ Email notification sent successfully",
        "recipient": recipient_email,
        "task": task_title,
        "status": "DEMO MODE - Check server logs"
    }

@router.post("/send-burnout-alert")
async def send_burnout_alert(
    manager_email: EmailStr,
    employee_name: str,
    risk_level: str,
    background_tasks: BackgroundTasks
):
    """Send email alert when employee burnout detected (DEMO MODE)"""
    
    html_content = f"""
    <h2>⚠️ Employee Burnout Alert!</h2>
    <p><strong>Employee:</strong> {employee_name}</p>
    <p><strong>Risk Level:</strong> {risk_level.upper()}</p>
    """
    
    background_tasks.add_task(
        mock_send_email,
        manager_email,
        f"⚠️ Burnout Alert: {employee_name}",
        html_content
    )
    
    return {
        "message": "✅ Burnout alert sent to manager",
        "recipient": manager_email,
        "employee": employee_name,
        "risk_level": risk_level,
        "status": "DEMO MODE - Check server logs"
    }
