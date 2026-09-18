from app.graph.state import SpendState
from database import AsyncSessionLocal
from models import Transaction
from sqlalchemy.future import select

async def deduplicate_transactions(state: SpendState) -> SpendState:
    """
    Deterministic deduplication:
    - Same source_message_id
    - Same merchant
    - Same amount
    This allows identical purchases on the same day if they come from different emails,
    while guaranteeing idempotency for re-runs of the same email.
    """
    validated = state.get("validated_transactions", [])
    if not validated:
        return state
        
    user_id = state.get("user_id")
    unique_transactions = []
    
    async with AsyncSessionLocal() as session:
        for tx in validated:
            source_message_id = tx.get("source_message_id")
            if not source_message_id:
                # Fallback if somehow missing
                unique_transactions.append(tx)
                continue
                
            # Check DB for duplicates from the EXACT SAME email with same merchant and amount
            query = await session.execute(
                select(Transaction)
                .where(
                    Transaction.user_id == user_id,
                    Transaction.source_message_id == source_message_id,
                    Transaction.merchant == tx["merchant"],
                    Transaction.amount == tx["amount"]
                )
            )
            existing = query.scalars().first()
            
            if not existing:
                unique_transactions.append(tx)
                
    return {
        "validated_transactions": unique_transactions
    }
