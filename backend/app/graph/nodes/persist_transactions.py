import logging
import uuid
from datetime import datetime
from sqlalchemy.future import select
from app.graph.state import SpendState
from database import AsyncSessionLocal
from models import Transaction, RawEmail

logger = logging.getLogger(__name__)

async def persist_transactions(state: SpendState) -> SpendState:
    """
    Save transactions to the database.
    - Validated transactions are saved with flagged = False
    - Errors (unvalidated transactions) are saved with flagged = True and flag_reason
    """
    logger.info("--- NODE: persist_transactions START ---")
    print("--- NODE: persist_transactions START ---")
    user_id_str = state.get("user_id")
    if not user_id_str:
        logger.error("No user_id in state.")
        return state

    validated = state.get("validated_transactions", [])
    errors = state.get("errors", [])
    
    if not validated and not errors:
        logger.info("No transactions to persist.")
        print("--- NODE: persist_transactions END (Saved 0) ---")
        return state

    saved_count = 0

    async with AsyncSessionLocal() as session:
        # Collect all source message IDs
        msg_ids = set()
        for tx in validated:
            if tx.get("source_message_id"):
                msg_ids.add(tx["source_message_id"])
        for err in errors:
            tx = err.get("transaction", {})
            if tx.get("source_message_id"):
                msg_ids.add(tx["source_message_id"])
                
        # Query RawEmail IDs
        raw_email_map = {}
        if msg_ids:
            result = await session.execute(
                select(RawEmail.gmail_message_id, RawEmail.id)
                .where(RawEmail.gmail_message_id.in_(list(msg_ids)))
            )
            for row in result.all():
                raw_email_map[row.gmail_message_id] = row.id

        transactions_to_insert = []
        
        def parse_date(date_str):
            if not date_str or str(date_str).lower() == "unknown":
                return None
            try:
                # Try simple ISO format or add more robust parsing if needed
                return datetime.strptime(str(date_str).split("T")[0], "%Y-%m-%d").date()
            except Exception:
                return None

        # 1. Validated
        for tx in validated:
            db_id = tx.get("db_id")
            if not db_id:
                continue
            
            uid = uuid.UUID(db_id) if isinstance(db_id, str) else db_id
            result = await session.execute(select(Transaction).where(Transaction.id == uid))
            db_tx = result.scalars().first()
            if db_tx:
                db_tx.merchant = tx.get("merchant", db_tx.merchant)
                db_tx.amount = tx.get("amount", db_tx.amount)
                db_tx.currency = tx.get("currency", db_tx.currency)
                db_tx.category = tx.get("category", db_tx.category)
                db_tx.date = parse_date(tx.get("transaction_date")) or db_tx.date
                db_tx.confidence = tx.get("confidence", db_tx.confidence)
                db_tx.flagged = False
                db_tx.flag_reason = None

        # 2. Not Validated
        for err in errors:
            if err.get("type") != "validation_failed":
                continue
                
            tx = err.get("transaction", {})
            db_id = tx.get("db_id")
            if not db_id:
                continue
                
            uid = uuid.UUID(db_id) if isinstance(db_id, str) else db_id
            result = await session.execute(select(Transaction).where(Transaction.id == uid))
            db_tx = result.scalars().first()
            if db_tx:
                db_tx.flagged = True
                db_tx.flag_reason = "validation_failed"
                
        await session.commit()
        saved_count = len(validated) + len(errors)
            
    logger.info(f"--- NODE: persist_transactions END (Saved {saved_count}) ---")
    print(f"--- NODE: persist_transactions END (Saved {saved_count}) ---")
    
    # Return empty lists to free up memory or signal completion
    return {
        "validated_transactions": [],
        "errors": []
    }
