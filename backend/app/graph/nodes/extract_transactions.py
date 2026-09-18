import logging
from app.graph.state import SpendState
from app.graph.schemas import TransactionExtraction
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


async def extract_transactions(state: SpendState) -> SpendState:
    """
    Extract structured transactions from financial emails.
    """
    logger.info("--- NODE: extract_transactions START ---")
    print("--- NODE: extract_transactions START ---")
    financial_emails = state.get("current_financial_emails", [])
    extracted_transactions = []
    
    gemini_service = GeminiService()
    llm = gemini_service.get_langchain_llm()
    structured_llm = llm.with_structured_output(TransactionExtraction)
    
    for email in financial_emails:
        print("----- Processing a email of subject : ",email.get('subject')," -------")
        prompt = f"""
        Extract financial transaction details from this email.
        Subject: {email.get('subject')}
        Snippet: {email.get('snippet')}
        Body: {email.get('body')}
        
        Important:
        - Never invent missing values.
        - Prefer transaction date over email received date when clearly available.
        - Handle Indian currency formats correctly (₹, Rs., INR).
        """
        try:
            res: TransactionExtraction = await structured_llm.ainvoke(prompt)
            # Add trace back to original email
            res_dict = res.model_dump()
            res_dict["source_message_id"] = email.get("message_id")
            res_dict["source_thread_id"] = email.get("thread_id")
            extracted_transactions.append(res_dict)
            print("----- Extracted transaction : ",res_dict," ------- ")
        except Exception as e:
            logger.error(f"Error extracting transaction from '{email.get('subject')}': {e}")
            print(f"----- ERROR extracting transaction '{email.get('subject')}': {e} -------")
    logger.info(f"--- NODE: extract_transactions END (Extracted {len(extracted_transactions)}) ---")
    print(f"--- NODE: extract_transactions END (Extracted {len(extracted_transactions)}) ---")
    return {
        "extracted_transactions": extracted_transactions,
        "transaction_count": state.get("transaction_count", 0) + len(extracted_transactions)
    }
