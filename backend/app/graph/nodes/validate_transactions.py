import uuid
import logging
from sqlalchemy.future import select
from app.graph.state import SpendState
from database import AsyncSessionLocal
from models import Transaction

logger = logging.getLogger(__name__)

async def validate_transactions(state: SpendState) -> SpendState:
    """
    Deterministically validate transactions.
    - Check amount >= 0
    - Check date exists
    - Check merchant exists
    """
    logger.info("--- NODE: validate_transactions START ---")
    print("--- NODE: validate_transactions START ---")
    extracted_transactions = state.get("extracted_transactions", [])
    validated = []
    errors = state.get("errors", [])
    
    async with AsyncSessionLocal() as session:
        for tx in extracted_transactions:
            is_valid = True
            
            # 1. Amount validation
            amount_val = tx.get("amount")
            if amount_val is None:
                print(f"Validation failed for {tx.get('merchant')}: amount is None")
                is_valid = False
            else:
                try:
                    amount_float = float(amount_val)
                    if amount_float < 0:
                        if tx.get("transaction_type") == "refund":
                            tx["amount"] = abs(amount_float)
                        else:
                            print(f"Validation failed for {tx.get('merchant')}: amount is negative ({amount_float}) and not a refund")
                            is_valid = False
                    else:
                        tx["amount"] = amount_float
                except (ValueError, TypeError):
                    print(f"Validation failed for {tx.get('merchant')}: amount is not a valid number ({amount_val})")
                    is_valid = False
                
            # 2. Date validation
            date_str = tx.get("transaction_date", "")
            if not date_str or str(date_str).lower() == "unknown":
                print(f"Validation failed for {tx.get('merchant')}: date is invalid ({date_str})")
                is_valid = False
                
            # 3. Merchant validation
            if not tx.get("merchant"):
                print(f"Validation failed for {tx.get('merchant')}: merchant is empty")
                is_valid = False
                
            # 4. Confidence
            confidence_val = tx.get("confidence", 0)
            try:
                confidence_float = float(confidence_val)
                if confidence_float < 0.6:
                    print(f"Validation failed for {tx.get('merchant')}: confidence too low ({confidence_float})")
                    is_valid = False
                tx["confidence"] = confidence_float
            except (ValueError, TypeError):
                print(f"Validation failed for {tx.get('merchant')}: confidence is not a valid number ({confidence_val})")
                is_valid = False
                
            # Update database if db_id is present
            db_id = tx.get("db_id")
            if db_id:
                try:
                    uid = uuid.UUID(db_id) if isinstance(db_id, str) else db_id
                    result = await session.execute(select(Transaction).where(Transaction.id == uid))
                    db_tx = result.scalars().first()
                    if db_tx:
                        if is_valid:
                            db_tx.flagged = False
                            db_tx.flag_reason = None
                        else:
                            db_tx.flagged = True
                            db_tx.flag_reason = "validation_failed"
                        # We can also update fields if they changed during validation (e.g., amount absolute value)
                        if "amount" in tx:
                            db_tx.amount = tx["amount"]
                except Exception as e:
                    logger.error(f"Error updating transaction {db_id}: {e}")
                    
            if is_valid:
                validated.append(tx)
            else:
                errors.append({"type": "validation_failed", "transaction": tx})
                
        await session.commit()
            
    logger.info(f"--- NODE: validate_transactions END (Validated {len(validated)}) ---")
    print(f"--- NODE: validate_transactions END (Validated {len(validated)}) ---")
    return {
        "validated_transactions": validated,
        "errors": errors
    }
