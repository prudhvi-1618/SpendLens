from typing import TypedDict, Annotated
import operator

class SpendState(TypedDict):
    user_id: str

    next_page_token: str | None

    current_message_ids: list[str]
    current_emails: list[dict]
    current_classifications: list[dict]
    current_financial_emails: list[dict]

    financial_emails: Annotated[list[dict], operator.add]
    extracted_transactions: Annotated[list[dict], operator.add]
    validated_transactions: Annotated[list[dict], operator.add]

    processed_email_count: int
    financial_email_count: int
    transaction_count: int

    errors: Annotated[list[dict], operator.add]

    total_spending: float
    category_summary: dict
    merchant_summary: dict

    recurring_payments: Annotated[list[dict], operator.add]
    anomalies: Annotated[list[dict], operator.add]
    insights: Annotated[list[dict], operator.add]

    sync_started_at: str | None
    sync_completed_at: str | None
