import logging
import asyncio
import json
from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, Query, Request, HTTPException
from fastapi.responses import StreamingResponse
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

@router.get("/sync/stream")
async def sync_stream(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    queue = asyncio.Queue()

    async def on_mail_found(mail):
        await queue.put({
            "event": "mail_found",
            "data": mail
        })

    async def run_graph():
        await queue.put({
            "event": "processing_started",
            "data": {"message": "Fetching mails..."}
        })
        try:
            initial_state = {
                "user_id": str(user.id),
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
            }
            # Run graph in background, passing the callback via config
            # using astream to emit node updates
            final_state = initial_state.copy()
            async for step in orchestrator.astream(
                initial_state,
                config={"configurable": {"on_mail_found": on_mail_found}}
            ):
                for node_name, node_output in step.items():
                    # Update final_state with the new output so we have it at the end
                    final_state.update(node_output)
                    
                    # Emit a node update event
                    node_display_names = {
                        "fetch_emails": "Fetched emails",
                        "classify_emails": "Classified emails",
                        "extract_transactions": "Extracted transactions",
                        "validate_transactions": "Validated transactions",
                        "deduplicate_transactions": "Deduplicated transactions",
                        "persist_transactions": "Persisted transactions",
                        "analyze_spending": "Analyzed spending",
                        "detect_recurring": "Detected recurring payments",
                        "detect_anomalies": "Detected anomalies",
                        "generate_insights": "Generated AI insights",
                    }
                    display_name = node_display_names.get(node_name, f"Completed {node_name}")
                    
                    await queue.put({
                        "event": "processing_started", # We reuse processing_started for status messages
                        "data": {"message": f"{display_name}...", "node": node_name}
                    })
                    
                    # Send node completed event with data so the frontend can populate the accordions
                    await queue.put({
                        "event": "node_completed",
                        "data": {
                            "node": node_name,
                            "extracted_transactions": node_output.get("extracted_transactions", []) if node_name == "extract_transactions" else []
                        }
                    })

            total_mails = final_state.get("processed_email_count", 0)
            await queue.put({
                "event": "processing_completed",
                "data": {"total_mails": total_mails}
            })
        except Exception as e:
            logger.error(f"Orchestrator pipeline failed in stream: {e}")
            await queue.put({"event": "error", "data": str(e)})
        finally:
            await queue.put(None)  # Sentinel to end stream

    # Start the graph execution
    task = asyncio.create_task(run_graph())

    async def event_generator():
        while True:
            msg = await queue.get()
            if msg is None:
                break
            yield f"event: {msg['event']}\ndata: {json.dumps(msg['data'])}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    gemini_service = GeminiService()
    llm = gemini_service.get_openrouter_llm()
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
