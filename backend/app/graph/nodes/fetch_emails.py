import logging
from datetime import datetime
from app.graph.state import SpendState
from database import AsyncSessionLocal
from models import User
from services.gmail_service import GmailService

logger = logging.getLogger(__name__)

async def fetch_emails(state: SpendState) -> SpendState:
    """
    Fetch a batch of emails from Gmail API using the current page token.
    Updates the next_page_token and current_emails.
    """
    logger.info("--- NODE: fetch_emails START ---")
    print("--- NODE: fetch_emails START ---")
    user_id = state.get("user_id")
    if not user_id:
        logger.error("No user_id in state.")
        logger.info("--- NODE: fetch_emails END (Error) ---")
        print("--- NODE: fetch_emails END (Error) ---")
        return state

    page_token = state.get("next_page_token")

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            logger.error(f"User {user_id} not found.")
            logger.info("--- NODE: fetch_emails END (Error) ---")
            print("--- NODE: fetch_emails END (Error) ---")
            return state

        gmail_service = GmailService(
            access_token=user.access_token,
            refresh_token=user.refresh_token,
            user_id=str(user.id),
            db=session
        )
        
        # Ensure token is valid
        await gmail_service.refresh_token_if_needed(user)
        
        # Fetch paginated batch
        raw_emails, next_page_token = await gmail_service.fetch_financial_emails(
            months_back=1, 
            page_token=page_token
        )
        
        # Format as needed
        current_emails = []
        for e in raw_emails:
            current_emails.append({
                "message_id": e["gmail_message_id"],
                "thread_id": e.get("gmail_thread_id", e["gmail_message_id"]),
                "subject": e["subject"],
                "snippet": e["snippet"],
                "body": e.get("body", ""),
                "received_at": e["received_at"].isoformat() if isinstance(e["received_at"], datetime) else e["received_at"]
            })
            
        logger.info(f"--- NODE: fetch_emails END (Fetched {len(current_emails)} emails) ---")
        print(f"--- NODE: fetch_emails END (Fetched {len(current_emails)} emails) ---")
        return {
            "current_emails": current_emails,
            "next_page_token": next_page_token,
            "processed_email_count": state.get("processed_email_count", 0) + len(current_emails)
        }
