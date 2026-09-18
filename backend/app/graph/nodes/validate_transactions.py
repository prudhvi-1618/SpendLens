import logging
from app.graph.state import SpendState

logger = logging.getLogger(__name__)
def validate_transactions(state: SpendState) -> SpendState:
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
    
    for tx in extracted_transactions:
        is_valid = True
        
        # 1. Amount validation
        if tx.get("amount") is None:
            is_valid = False
        else:
            if tx["amount"] < 0:
                if tx.get("transaction_type") == "refund":
                    tx["amount"] = abs(tx["amount"])
                else:
                    is_valid = False
            
        # 2. Date validation
        if not tx.get("transaction_date"):
            is_valid = False
            
        # 3. Merchant validation
        if not tx.get("merchant"):
            is_valid = False
            
        # 4. Confidence
        if tx.get("confidence", 0) < 0.6:
            is_valid = False
            
        if is_valid:
            validated.append(tx)
        else:
            errors.append({"type": "validation_failed", "transaction": tx})
            
    logger.info(f"--- NODE: validate_transactions END (Validated {len(validated)}) ---")
    print(f"--- NODE: validate_transactions END (Validated {len(validated)}) ---")
    return {
        "validated_transactions": validated,
        "errors": errors
    }
