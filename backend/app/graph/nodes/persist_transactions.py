from datetime import datetime
from app.graph.state import SpendState
from database import AsyncSessionLocal
from models import Transaction

async def persist_transactions(state: SpendState) -> SpendState:
    """
    Save validated and deduplicated transactions to the database.
    """
    transactions = state.get("validated_transactions", [])
    if not transactions:
        return state
        
    user_id = state.get("user_id")
    
    async with AsyncSessionLocal() as session:
        for tx in transactions:
            try:
                date_val = None
                if tx.get("transaction_date"):
                    date_val = datetime.strptime(tx["transaction_date"], "%Y-%m-%d").date()
                    
                new_tx = Transaction(
                    user_id=user_id,
                    merchant=tx.get("merchant"),
                    amount=tx.get("amount"),
                    currency=tx.get("currency"),
                    category=tx.get("category"),
                    date=date_val,
                    transaction_type=tx.get("transaction_type", "unknown"),
                    status=tx.get("status", "unknown"),
                    source_message_id=tx.get("source_message_id"),
                    source_thread_id=tx.get("source_thread_id"),
                    description=tx.get("description"),
                    confidence=tx.get("confidence", 0)
                )
                session.add(new_tx)
            except Exception as e:
                # Log or handle
                pass
                
        await session.commit()
        
    return {
        "validated_transactions": [] # Clear to free up memory for next batch
    }
