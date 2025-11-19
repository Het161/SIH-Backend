"""
Email Service for SmartWork 360
Handles all email sending functionality
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    content: str,
    from_email: str = None,
    from_name: str = None
):
    """
    Send email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        content: Email content (HTML)
        from_email: Sender email (optional, uses settings.EMAIL_FROM)
        from_name: Sender name (optional, uses settings.EMAIL_FROM_NAME)
    """
    try:
        # Use defaults from settings if not provided
        sender_email = from_email or settings.EMAIL_FROM
        sender_name = from_name or settings.EMAIL_FROM_NAME
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{sender_name} <{sender_email}>"
        message["To"] = to_email
        
        # Add HTML content
        html_part = MIMEText(content, "html")
        message.attach(html_part)
        
        # Send email using STARTTLS (port 587)
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,  # Use STARTTLS
            timeout=10,  # 10 second timeout
        )
        
        logger.info(f"✅ Email sent successfully to: {to_email}")
        return True
        
    except aiosmtplib.SMTPException as e:
        logger.error(f"❌ SMTP error sending email to {to_email}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
        raise


async def send_welcome_email(user_email: str, user_name: str):
    """Send welcome email to new user"""
    subject = "Welcome to SmartWork 360"
    content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">Welcome to SmartWork 360!</h2>
            <p>Hi {user_name},</p>
            <p>Your account has been successfully created.</p>
            <p><strong>Email:</strong> {user_email}</p>
            <p>You can now login to the SmartWork 360 system and start managing your productivity.</p>
            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="font-size: 12px; color: #6b7280;">
                This is an automated message. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    return await send_email(user_email, subject, content)


async def send_password_reset_email(user_email: str, user_name: str, reset_token: str):
    """Send password reset email"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    subject = "Password Reset Request"
    content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">Password Reset Request</h2>
            <p>Hi {user_name},</p>
            <p>We received a request to reset your password.</p>
            <p>Click the button below to reset your password:</p>
            <p style="margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #2563eb; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="font-size: 12px; color: #6b7280; word-break: break-all;">
                {reset_url}
            </p>
            <p style="margin-top: 30px; color: #dc2626;">
                If you didn't request this, please ignore this email.
            </p>
            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="font-size: 12px; color: #6b7280;">
                This link will expire in 1 hour.
            </p>
        </div>
    </body>
    </html>
    """
    
    return await send_email(user_email, subject, content)
