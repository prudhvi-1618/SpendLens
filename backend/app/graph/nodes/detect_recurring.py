from datetime import timedelta
import uuid
from app.graph.state import SpendState
from database import AsyncSessionLocal
from models import Transaction
from sqlalchemy.future import select

async def detect_recurring(state: SpendState) -> SpendState:
    """
    Deterministic detection of recurring payments.
    """
    user_id = state.get("user_id")
    uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    recurring_payments = []
    
    async with AsyncSessionLocal() as session:
        # Fetch all grouped by merchant where type is subscription or frequent bills
        query = await session.execute(
            select(Transaction)
            .where(
                Transaction.user_id == uid,
                Transaction.flagged == False
            )
            .order_by(Transaction.merchant, Transaction.date.desc())
        )
        
        transactions = query.scalars().all()
        
    merchant_groups = {}
    for tx in transactions:
        if not tx.merchant or not tx.date:
            continue
        if tx.merchant not in merchant_groups:
            merchant_groups[tx.merchant] = []
        merchant_groups[tx.merchant].append(tx)
        
    for merchant, txs in merchant_groups.items():
        is_explicit_subscription = any(tx.category and tx.category.lower() == "subscription" for tx in txs)
        min_tx = 2 if is_explicit_subscription else 3
        
        if len(txs) >= min_tx:
            # Check for regular intervals (e.g., monthly)
            # Simplistic approach: average gap between payments
            intervals = []
            for i in range(len(txs)-1):
                gap = (txs[i].date - txs[i+1].date).days
                intervals.append(gap)
                
            avg_gap = sum(intervals) / len(intervals)
            
            if 25 <= avg_gap <= 35:
                frequency = "monthly"
            elif 350 <= avg_gap <= 380:
                frequency = "yearly"
            elif 6 <= avg_gap <= 8:
                frequency = "weekly"
            else:
                frequency = "irregular"
                
            if frequency != "irregular":
                recurring_payments.append({
                    "merchant": merchant,
                    "typical_amount": float(txs[0].amount) if txs[0].amount else 0.0,
                    "frequency": frequency,
                    "last_payment": txs[0].date.isoformat(),
                    "confidence": 0.9 if len(txs) > 2 else 0.6
                })
                
    return {
        "recurring_payments": recurring_payments
    }
