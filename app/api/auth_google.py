from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import os

router = APIRouter(prefix="/api/auth", tags=["Google Auth"])

# OAuth Config
config = Config(environ={
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID', 'your-client-id'),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET', 'your-secret'),
})

oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get('/google/login')
async def google_login(request: Request):
    """Redirect to Google login"""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/google/callback')
async def google_callback(request: Request):
    """Handle Google callback"""
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')
    
    # user_info contains: email, name, picture, sub (Google ID)
    return {
        "email": user_info['email'],
        "name": user_info['name'],
        "picture": user_info['picture'],
        "google_id": user_info['sub']
    }
