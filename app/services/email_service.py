# app/services/email_service.py
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = ""
) -> bool:
    """
    Send email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML body of email
        text_content: Plain text alternative (optional)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add plain text part
        if text_content:
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)
        
        # Add HTML part
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        
        logger.info(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False


async def send_welcome_email(
    user_email: str,
    user_name: str,
    user_role: str,
    user_department: str
) -> bool:
    """
    Send welcome email to newly registered user
    """
    
    subject = f"🎉 Welcome to SmartWork 360, {user_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .info-box {{
                background: white;
                padding: 15px;
                border-left: 4px solid #667eea;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Welcome to SmartWork 360!</h1>
        </div>
        
        <div class="content">
            <h2>Hi {user_name},</h2>
            
            <p>Thank you for joining <strong>SmartWork 360</strong> - your intelligent productivity companion! We're excited to have you on board.</p>
            
            <div class="info-box">
                <h3>📋 Your Account Details:</h3>
                <p><strong>Name:</strong> {user_name}</p>
                <p><strong>Email:</strong> {user_email}</p>
                <p><strong>Role:</strong> {user_role.title()}</p>
                <p><strong>Department:</strong> {user_department}</p>
            </div>
            
            <h3>🎯 What's Next?</h3>
            <ul>
                <li>✅ Complete your profile</li>
                <li>📊 Explore your personalized dashboard</li>
                <li>🤖 Try our AI-powered task assistant</li>
                <li>📈 Track your productivity in real-time</li>
            </ul>
            
            <center>
                <a href="{settings.FRONTEND_URL}/login" class="button">
                    🚀 Get Started Now
                </a>
            </center>
            
            <h3>💡 Quick Tips:</h3>
            <p>• Use the dashboard to view all your tasks at a glance</p>
            <p>• Enable notifications to stay updated on task assignments</p>
            <p>• Upload evidence to tasks for better transparency</p>
            
            <p style="margin-top: 30px;">If you have any questions, feel free to reply to this email or contact our support team.</p>
            
            <p><strong>Happy productivity tracking! 🎉</strong></p>
            
            <p>Best regards,<br>
            <strong>The SmartWork 360 Team</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated message. Please do not reply directly to this email.</p>
            <p>&copy; 2025 SmartWork 360. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to SmartWork 360, {user_name}!
    
    Thank you for joining SmartWork 360 - your intelligent productivity companion!
    
    Your Account Details:
    - Name: {user_name}
    - Email: {user_email}
    - Role: {user_role.title()}
    - Department: {user_department}
    
    Get started: {settings.FRONTEND_URL}/login
    
    Best regards,
    The SmartWork 360 Team
    """
    
    return await send_email(user_email, subject, html_content, text_content)


async def send_task_assignment_email(
    user_email: str,
    user_name: str,
    task_title: str,
    task_description: str,
    due_date: str
) -> bool:
    """
    Send email notification when a task is assigned
    """
    
    subject = f"📋 New Task Assigned: {task_title}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
            }}
            .task-box {{
                background: #f0f7ff;
                padding: 20px;
                border-left: 4px solid #2196F3;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <h2>Hi {user_name},</h2>
        <p>You have been assigned a new task:</p>
        
        <div class="task-box">
            <h3>📋 {task_title}</h3>
            <p><strong>Description:</strong> {task_description}</p>
            <p><strong>Due Date:</strong> {due_date}</p>
        </div>
        
        <p><a href="{settings.FRONTEND_URL}/tasks" style="background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Task</a></p>
        
        <p>Best regards,<br>SmartWork 360 Team</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Hi {user_name},
    
    You have been assigned a new task:
    
    Task: {task_title}
    Description: {task_description}
    Due Date: {due_date}
    
    View your task at: {settings.FRONTEND_URL}/tasks
    
    Best regards,
    SmartWork 360 Team
    """
    
    return await send_email(user_email, subject, html_content, text_content)





