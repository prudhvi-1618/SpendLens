from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from database import get_db, AsyncSessionLocal
from models import User, RawEmail
from services.gmail_service import GmailService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emails", tags=["emails"])

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def run_sync(user_id: str, access_token: str, refresh_token: str):
    logger.info("Background email sync started for user %s", user_id)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user:
            service = GmailService(access_token, refresh_token, user_id, db)
            await service.refresh_token_if_needed(user)
            await service.sync_to_db()
    logger.info("Background email sync finished for user %s", user_id)

@router.post("/sync")
async def sync_emails(background_tasks: BackgroundTasks, user: User = Depends(get_current_user)):
    background_tasks.add_task(run_sync, str(user.id), user.access_token, user.refresh_token)
    return {"status": "sync started", "message": "Email synchronization is running in the background."}

@router.get("/status")
async def email_status(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count()).select_from(RawEmail).where(RawEmail.user_id == user.id))
    total_emails = total_result.scalar() or 0
    
    processed_result = await db.execute(select(func.count()).select_from(RawEmail).where(RawEmail.user_id == user.id, RawEmail.processed == True))
    processed_emails = processed_result.scalar() or 0
    
    return {
        "total_emails": total_emails,
        "processed_emails": processed_emails
    }
