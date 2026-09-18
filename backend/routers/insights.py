import logging
from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from database import get_db
from models import Transaction, RawEmail
from routers.auth import get_me  # Ensure this works or rewrite dependency
from app.graph.graph import orchestrator
from datetime import datetime
from services.gemini_service import GeminiService
from agents.spend_profiler import SpendProfiler
from models import User
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def run_extraction(user_id: str):
    try:
        await orchestrator.ainvoke({
            "user_id": user_id,
            "next_page_token": None,
            "current_message_ids": [],
            "current_emails": [],
            "current_classifications": [],
            "current_financial_emails": [],
            "financial_emails": [],
            "extracted_transactions": [],
            "validated_transactions": [],
            "processed_email_count": 0,
            "financial_email_count": 0,
            "transaction_count": 0,
            "errors": [],
            "total_spending": 0.0,
            "category_summary": {},
            "merchant_summary": {},
            "recurring_payments": [],
            "anomalies": [],
            "insights": [],
            "sync_started_at": datetime.utcnow().isoformat(),
            "sync_completed_at": None,
        })
    except Exception as e:
        logger.error(f"Orchestrator pipeline failed: {e}")

@router.post("/sync")
async def sync_insights(background_tasks: BackgroundTasks, user: User = Depends(get_current_user)):
    background_tasks.add_task(run_extraction, str(user.id))
    return {"status": "processing", "message": "Extraction pipeline started"}

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    gemini_service = GeminiService()
    llm = gemini_service.get_langchain_llm()
    profiler = SpendProfiler(llm)
    profile = await profiler.build_profile(str(user.id), db)
    return profile

@router.get("/anomalies")
async def get_anomalies(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = (
        select(Transaction, RawEmail.gmail_message_id)
        .join(RawEmail, Transaction.raw_email_id == RawEmail.id)
        .where(Transaction.user_id == user.id, Transaction.flagged == True)
        .order_by(Transaction.date.desc())
    )
    result = await db.execute(query)
    
    anomalies = []
    for tx, msg_id in result.all():
        anomalies.append({
            "id": str(tx.id),
            "merchant": tx.merchant,
            "amount": float(tx.amount) if tx.amount else 0,
            "currency": tx.currency,
            "date": tx.date,
            "category": tx.category,
            "flag_reason": tx.flag_reason,
            "gmail_message_id": msg_id
        })
    return anomalies

@router.get("/transactions")
async def get_transactions(
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    base_query = select(Transaction).where(Transaction.user_id == user.id)
    count_query = select(func.count()).select_from(Transaction).where(Transaction.user_id == user.id)
    
    if category:
        base_query = base_query.where(Transaction.category == category)
        count_query = count_query.where(Transaction.category == category)
    if merchant:
        base_query = base_query.where(Transaction.merchant.ilike(f"%{merchant}%"))
        count_query = count_query.where(Transaction.merchant.ilike(f"%{merchant}%"))
    if date_from:
        base_query = base_query.where(Transaction.date >= date_from)
        count_query = count_query.where(Transaction.date >= date_from)
    if date_to:
        base_query = base_query.where(Transaction.date <= date_to)
        count_query = count_query.where(Transaction.date <= date_to)
        
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    pages = (total + limit - 1) // limit
    
    query = base_query.order_by(Transaction.date.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    
    items = []
    for tx in result.scalars().all():
        items.append({
            "id": str(tx.id),
            "merchant": tx.merchant,
            "amount": float(tx.amount) if tx.amount else 0,
            "currency": tx.currency,
            "category": tx.category,
            "date": tx.date,
            "confidence": tx.confidence,
            "flagged": tx.flagged,
            "flag_reason": tx.flag_reason
        })
        
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages
    }
