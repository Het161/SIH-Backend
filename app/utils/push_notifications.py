import firebase_admin
from firebase_admin import credentials, messaging
import os

# Initialize Firebase (download service account JSON from Firebase Console)
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

async def send_push_notification(
    device_token: str,
    title: str,
    body: str,
    data: dict = None
):
    """Send push notification to device"""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        token=device_token,
    )
    
    response = messaging.send(message)
    return {"success": True, "message_id": response}
