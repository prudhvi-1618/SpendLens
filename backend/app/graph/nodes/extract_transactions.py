import logging
from datetime import datetime
from sqlalchemy.future import select
from app.graph.state import SpendState
from app.graph.schemas import TransactionExtraction
from services.gemini_service import GeminiService
from database import AsyncSessionLocal
from models import Transaction, RawEmail

logger = logging.getLogger(__name__)

async def extract_transactions(state: SpendState) -> SpendState:
    """
    Extract structured transactions from financial emails and save to DB as not validated.
    """
    logger.info("--- NODE: extract_transactions START ---")
    print("--- NODE: extract_transactions START ---")
    financial_emails = state.get("current_financial_emails", [])
    extracted_transactions = []
    user_id_str = state.get("user_id")
    
    gemini_service = GeminiService()
    llm = gemini_service.get_openrouter_llm()
    structured_llm = llm.with_structured_output(TransactionExtraction)
    
    async with AsyncSessionLocal() as session:
        for email in financial_emails:
            print("----- Processing a email of subject : ",email.get('subject')," -------")
            prompt = f"""
            Extract financial transaction details from this email.
            Subject: {email.get('subject')}
            Email Date: {email.get('received_at')}
            Snippet: {email.get('snippet')}
            Body: {email.get('body')}
            
            Important:
            - Never invent missing values.
            - Prefer transaction date over email received date when clearly available. If missing, fallback to Email Date.
            - Provide dates in YYYY-MM-DD format.
            - Carefully extract the exact transaction amount. Look for numbers near 'Paid', 'Total', 'Amount', or currency symbols.
            - Handle Indian currency formats correctly (₹, Rs., INR).
            """
            try:
                res = await structured_llm.ainvoke(prompt)
                
                # Sometimes LangChain/Gemini returns a list of results instead of a single object
                if isinstance(res, list):
                    if len(res) == 0:
                        print(f"----- Warning: empty extraction result for '{email.get('subject')}' -------")
                        continue
                    res = res[0]
                
                # Handle both dict (if parsed as json) and Pydantic model
                if isinstance(res, dict):
                    # Langchain sometimes returns a tool call dict e.g. {'args': {...}, 'type': '...'}
                    if "args" in res and isinstance(res["args"], dict):
                        res_dict = res["args"]
                    else:
                        res_dict = res
                else:
                    res_dict = res.model_dump()
                    
                # Add trace back to original email
                msg_id = email.get("message_id")
                res_dict["source_message_id"] = msg_id
                res_dict["source_thread_id"] = email.get("thread_id")
                
                # Fallback to received_at if transaction_date is missing
                if not res_dict.get("transaction_date") or str(res_dict.get("transaction_date")).lower() == "unknown":
                    res_dict["transaction_date"] = email.get("received_at")

                # Save to DB as not validated
                raw_email_result = await session.execute(
                    select(RawEmail).where(RawEmail.gmail_message_id == msg_id)
                )
                raw_email = raw_email_result.scalars().first()
                
                if raw_email and user_id_str:
                    date_val = None
                    date_str = res_dict.get("transaction_date")
                    if date_str and str(date_str).lower() != "unknown":
                        try:
                            date_val = datetime.strptime(str(date_str).split("T")[0], "%Y-%m-%d").date()
                        except Exception:
                            pass
                            
                    import uuid
                    uid = uuid.UUID(user_id_str) if isinstance(user_id_str, str) else user_id_str
                    db_tx = Transaction(
                        user_id=uid,
                        raw_email_id=raw_email.id,
                        merchant=res_dict.get("merchant", "Unknown"),
                        amount=res_dict.get("amount", 0.0),
                        currency=res_dict.get("currency", "INR"),
                        category=res_dict.get("category", "Uncategorized"),
                        date=date_val,
                        confidence=res_dict.get("confidence", 0.0),
                        flagged=True,
                        flag_reason="not_validated"
                    )
                    session.add(db_tx)
                    await session.flush() # Get the generated DB ID
                    res_dict["db_id"] = str(db_tx.id)
                    
                extracted_transactions.append(res_dict)
                print("----- Extracted transaction : ",res_dict," ------- ")
            except Exception as e:
                logger.error(f"Error extracting transaction from '{email.get('subject')}': {e}")
                print(f"----- ERROR extracting transaction '{email.get('subject')}': {e} -------")
                
        await session.commit()
        
    logger.info(f"--- NODE: extract_transactions END (Extracted {len(extracted_transactions)}) ---")
    print(f"--- NODE: extract_transactions END (Extracted {len(extracted_transactions)}) ---")
    return {
        "extracted_transactions": extracted_transactions,
        "transaction_count": state.get("transaction_count", 0) + len(extracted_transactions)
    }
