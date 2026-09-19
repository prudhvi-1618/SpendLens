from datetime import timedelta, datetime
import uuid
import logging
from app.graph.state import SpendState
from database import AsyncSessionLocal
from models import Transaction
from sqlalchemy.future import select
from sqlalchemy import func

logger = logging.getLogger(__name__)

async def detect_anomalies(state: SpendState) -> SpendState:
    """
    Deterministic anomaly detection (amount spikes, new merchants).
    """
    logger.info("--- NODE: detect_anomalies START ---")
    print("--- NODE: detect_anomalies START ---")
    user_id = state.get("user_id")
    uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    anomalies = []
    
    async with AsyncSessionLocal() as session:
        # Get recent transactions (e.g., from this sync)
        # For this simplified version, let's just re-evaluate all completed tx from the last 7 days against 90 day baseline
        seven_days_ago = datetime.utcnow().date() - timedelta(days=7)
        recent_query = await session.execute(
            select(Transaction)
            .where(
                Transaction.user_id == uid,
                Transaction.date >= seven_days_ago
            )
        )
        recent_txs = recent_query.scalars().all()
        
        for tx in recent_txs:
            if not tx.merchant or not tx.amount:
                continue
                
            amount = float(tx.amount)
            
            # 1. Amount Anomaly
            ninety_days_ago = tx.date - timedelta(days=90)
            baseline_query = await session.execute(
                select(Transaction.amount)
                .where(
                    Transaction.user_id == uid,
                    Transaction.merchant == tx.merchant,
                    Transaction.date >= ninety_days_ago,
                    Transaction.id != tx.id
                )
            )
            historical_amounts = [float(a) for a in baseline_query.scalars().all() if a is not None]
            
            flagged = False
            if len(historical_amounts) >= 2:
                avg_hist = sum(historical_amounts) / len(historical_amounts)
                if avg_hist > 0 and amount > 2.0 * avg_hist:
                    flagged = True
                    anomalies.append({
                        "transaction_id": str(tx.id),
                        "type": "amount_anomaly",
                        "severity": "high" if amount > 3.0 * avg_hist else "medium",
                        "reason": f"Amount ₹{amount:.0f} is {(amount/avg_hist):.1f}x your usual ₹{avg_hist:.0f} at {tx.merchant}",
                        "merchant": tx.merchant
                    })
                    
            # 2. New Merchant
            if not flagged and amount >= 2000:
                merchant_count = await session.execute(
                    select(func.count())
                    .select_from(Transaction)
                    .where(
                        Transaction.user_id == uid,
                        Transaction.merchant == tx.merchant,
                        Transaction.id != tx.id
                    )
                )
                count = merchant_count.scalar() or 0
                if count == 0:
                    anomalies.append({
                        "transaction_id": str(tx.id),
                        "type": "new_merchant",
                        "severity": "medium",
                        "reason": f"First-ever payment of ₹{amount:.0f} to {tx.merchant}",
                        "merchant": tx.merchant
                    })

    return {
        "anomalies": anomalies
    }
