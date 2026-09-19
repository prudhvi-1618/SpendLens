import uuid
from app.graph.state import SpendState
from database import AsyncSessionLocal
from models import Transaction
from sqlalchemy.future import select
from sqlalchemy import func

# Simple static exchange rates for demo purposes. Base currency = INR
EXCHANGE_RATES = {
    "USD": 83.0,
    "EUR": 90.0,
    "GBP": 105.0,
    "INR": 1.0
}

async def analyze_spending(state: SpendState) -> SpendState:
    """
    Deterministic spending analysis (Total, Category, Merchant) using SQL.
    Normalizes amounts to INR.
    """
    user_id = state.get("user_id")
    uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    
    total_spending = 0.0
    category_summary = {}
    merchant_summary = {}
    
    async with AsyncSessionLocal() as session:
        # Get all completed purchases/bills/payments
        query = await session.execute(
            select(
                Transaction.merchant,
                Transaction.category,
                Transaction.amount,
                Transaction.currency
            )
            .where(
                Transaction.user_id == uid,
                Transaction.flagged == False
            )
        )
        
        for merchant, category, amount, currency in query:
            if amount is None:
                continue
            
            curr = (currency or "INR").upper()
            rate = EXCHANGE_RATES.get(curr, 1.0)
            amt = float(amount) * rate
            
            total_spending += amt
            
            # Category sum
            cat = category or "other"
            category_summary[cat] = category_summary.get(cat, 0.0) + amt
            
            # Merchant sum
            merch = merchant or "Unknown"
            merchant_summary[merch] = merchant_summary.get(merch, 0.0) + amt
            
        # Refund processing (subtract from totals if deterministic rules apply)
        refund_query = await session.execute(
            select(
                Transaction.merchant, 
                Transaction.category, 
                Transaction.amount, 
                Transaction.currency
            )
            .where(
                Transaction.user_id == uid,
                Transaction.flagged == False,
                Transaction.amount < 0
            )
        )
        for merchant, category, amount, currency in refund_query:
            if amount is None:
                continue
                
            curr = (currency or "INR").upper()
            rate = EXCHANGE_RATES.get(curr, 1.0)
            amt = float(amount) * rate
            
            total_spending -= amt
            
            cat = category or "other"
            if cat in category_summary:
                category_summary[cat] -= amt
            
            merch = merchant or "Unknown"
            if merch in merchant_summary:
                merchant_summary[merch] -= amt
                
    return {
        "total_spending": total_spending,
        "category_summary": category_summary,
        "merchant_summary": merchant_summary
    }
