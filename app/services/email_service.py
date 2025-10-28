import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Welcome Email Template
WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }
        .content {
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white !important;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        ul li {
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to SmartWork 360!</h1>
        </div>
        <div class="content">
            <h2>Hello {{ name }}! 👋</h2>
            <p>We're excited to have you on board! You've successfully signed in to your SmartWork 360 account.</p>
            
            <p><strong>Your Account Details:</strong></p>
            <ul>
                <li><strong>Email:</strong> {{ email }}</li>
                <li><strong>Role:</strong> {{ role }}</li>
                <li><strong>Department:</strong> {{ department }}</li>
            </ul>
            
            <p>You can now start managing your tasks, tracking productivity, and collaborating with your team!</p>
            
            <div style="text-align: center;">
                <a href="{{ app_url }}" class="button">Go to Dashboard →</a>
            </div>
            
            <p style="margin-top: 30px;">If you have any questions, feel free to reach out to our support team.</p>
            
            <p>Happy working!<br>
            <strong>The SmartWork 360 Team</strong></p>
        </div>
        <div class="footer">
            <p>© 2025 SmartWork 360. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""


async def send_email(to_email: str, subject: str, html_content: str):
    """Send email using SMTP"""
    try:
        # Skip if email not configured
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("⚠️ Email not configured. Skipping email send.")
            return False
        
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM or settings.SMTP_USER}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add HTML content
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
        logger.error(f"❌ Failed to send email to {to_email}: {e}")
        return False


async def send_welcome_email(user_email: str, user_name: str, user_role: str, user_department: str):
    """Send welcome email on sign in"""
    try:
        # Render template
        template = Template(WELCOME_EMAIL_TEMPLATE)
        html_content = template.render(
            name=user_name,
            email=user_email,
            role=user_role.capitalize(),
            department=user_department or "Not specified",
            app_url=settings.FRONTEND_URL or "http://localhost:3000"
        )
        
        # Send email
        await send_email(
            to_email=user_email,
            subject="🎉 Welcome to SmartWork 360!",
            html_content=html_content
        )
        
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")


