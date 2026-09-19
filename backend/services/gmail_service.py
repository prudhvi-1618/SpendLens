import os
import httpx
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models import User, RawEmail
from routers.auth import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

FINANCIAL_SEARCH_TERMS = [
    "receipt",
    "invoice",
    "payment",
    "paid",
    "charged",
    "purchase",
    "transaction",
    "billing",
    "subscription",
    "renewal",
    "refund",
    '"order confirmation"',
    '"amount due"',
    '"payment successful"',
    '"card ending"',
    '"credit card"',
    '"debit card"',
    "upi",
    "autopay",
]

class GmailService:
    def __init__(self, access_token: str, refresh_token: str, user_id: str, db: AsyncSession):
        self.access_token = decrypt_token(access_token)
        self.refresh_token = decrypt_token(refresh_token)
        self.user_id = user_id
        self.db = db

    async def refresh_token_if_needed(self, user: User):
        if user.token_expiry - datetime.utcnow() < timedelta(minutes=5):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token",
                    }
                )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                user.access_token = encrypt_token(self.access_token)
                user.token_expiry = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
                await self.db.commit()
            else:
                logger.error(f"Failed to refresh token: {response.text}")

    @staticmethod
    def build_financial_query(months_back: int) -> str:
        date_limit = (datetime.utcnow() - timedelta(days=30 * months_back)).strftime("%Y/%m/%d")
        search_terms = " OR ".join(FINANCIAL_SEARCH_TERMS)
        return f"after:{date_limit} ({search_terms})"

    async def fetch_financial_emails(
        self,
        months_back: int = 6,
        page_token: str | None = None,
        max_results: int = 200,
        on_mail_found=None,
    ) -> tuple[list[dict], str | None]:
        query = self.build_financial_query(months_back)
        logger.info("Searching Gmail with query: %s", query)
        emails = []
        async with httpx.AsyncClient() as client:
            params = {"q": query, "maxResults": max_results}
            if page_token:
                params["pageToken"] = page_token

            list_resp = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params=params
            )
            list_data = list_resp.json() if list_resp.content else {}
            logger.info(
                "Gmail search response: status=%s resultSizeEstimate=%s",
                list_resp.status_code,
                list_data.get("resultSizeEstimate"),
            )
            if list_resp.status_code != 200:
                logger.error(f"Failed to list messages: {list_resp.text}")
                return emails, None

            messages = list_data.get("messages", [])
            next_page_token = list_data.get("nextPageToken")
            logger.info("Gmail returned %d matching messages for user %s", len(messages), self.user_id)
            
            for index, msg in enumerate(messages, start=1):
                msg_id = msg["id"]
                msg_resp = await client.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"format": "metadata", "metadataHeaders": ["Subject"]}
                )
                
                if msg_resp.status_code == 200:
                    msg_data = msg_resp.json()
                    headers = msg_data.get("payload", {}).get("headers", [])
                    subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
                    internal_date = msg_data.get("internalDate")
                    received_at = datetime.fromtimestamp(int(internal_date) / 1000.0) if internal_date else datetime.utcnow()
                    email = {
                        "user_id": self.user_id,
                        "gmail_message_id": msg_id,
                        "subject": subject,
                        "snippet": msg_data.get("snippet", ""),
                        "received_at": received_at
                    }
                    emails.append(email)
                    
                    if on_mail_found:
                        # Extract sender if possible, else default to Unknown
                        sender_header = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown")
                        sender = sender_header.split("<")[0].strip() if "<" in sender_header else sender_header
                        
                        await on_mail_found({
                            "id": msg_id,
                            "subject": subject,
                            "sender": sender,
                            "date": received_at.isoformat() if hasattr(received_at, "isoformat") else str(received_at),
                            "mail_link": f"https://mail.google.com/mail/u/0/#all/{msg_id}"
                        })
                        
                    logger.info(
                        "Fetched email %d/%d: id=%s subject=%r",
                        index,
                        len(messages),
                        msg_id,
                        subject,
                    )
                else:
                    logger.warning(
                        "Failed to fetch email %d/%d: id=%s status=%s",
                        index,
                        len(messages),
                        msg_id,
                        msg_resp.status_code,
                    )
        return emails, next_page_token

    async def sync_to_db(self):
        try:
            logger.info("Starting Gmail sync for user %s", self.user_id)
            emails, _ = await self.fetch_financial_emails()
            if not emails:
                logger.info("No Gmail messages found for user %s", self.user_id)
                return
            
            stmt = insert(RawEmail).values(emails)
            stmt = stmt.on_conflict_do_nothing(index_elements=['gmail_message_id'])
            
            result = await self.db.execute(stmt)
            await self.db.commit()
            logger.info(
                "Saved %d new emails to raw_emails for user %s",
                result.rowcount or 0,
                self.user_id,
            )
        except Exception as e:
            logger.error(f"Error syncing emails: {e}")
