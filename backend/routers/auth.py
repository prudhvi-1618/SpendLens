import os
import httpx
import base64
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from cryptography.fernet import Fernet

from database import get_db
from models import User

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key-must-be-changed")
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Generate standard 32-byte url-safe base64 key for Fernet from the SECRET_KEY
fernet_key = base64.urlsafe_b64encode(hashlib.sha256(SECRET_KEY.encode()).digest())
cipher_suite = Fernet(fernet_key)

def encrypt_token(token: str) -> str:
    if not token:
        return token
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    if not encrypted_token:
        return encrypted_token
    return cipher_suite.decrypt(encrypted_token.encode()).decode()

@router.get("/google")
async def google_auth():
    redirect_uri = f"{API_URL}/auth/callback"
    scope = "openid email profile https://www.googleapis.com/auth/gmail.readonly"
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&scope={scope}&"
        f"access_type=offline&prompt=consent"
    )
    return {"url": auth_url}

@router.get("/callback")
async def google_auth_callback(request: Request, code: str, db: AsyncSession = Depends(get_db)):
    redirect_uri = f"{API_URL}/auth/callback"
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
        )
        
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange token")
        
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
    if user_info_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")
        
    user_info = user_info_response.json()
    google_id = user_info.get("id")
    email = user_info.get("email")
    
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalars().first()
    
    token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
    
    if user:
        user.access_token = encrypt_token(access_token)
        if refresh_token:
            user.refresh_token = encrypt_token(refresh_token)
        user.token_expiry = token_expiry
    else:
        user = User(
            google_id=google_id,
            email=email,
            access_token=encrypt_token(access_token),
            refresh_token=encrypt_token(refresh_token) if refresh_token else None,
            token_expiry=token_expiry
        )
        db.add(user)
        
    await db.commit()
    await db.refresh(user)
    
    request.session["user_id"] = str(user.id)
    return RedirectResponse(url=f"{FRONTEND_URL}/dashboard")

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"status": "ok"}

@router.get("/me")
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        request.session.clear()
        raise HTTPException(status_code=401, detail="User not found")
        
    return {"id": str(user.id), "email": user.email}
