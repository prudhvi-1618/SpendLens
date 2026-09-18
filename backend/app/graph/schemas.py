from typing import Literal

from pydantic import BaseModel

class TransactionExtraction(BaseModel):
    merchant: str | None
    amount: float | None
    currency: str | None
    transaction_date: str | None
    category: str | None
    transaction_type: Literal[
        "purchase",
        "subscription",
        "bill",
        "refund",
        "payment",
        "other"
    ] | None
    status: Literal[
        "completed",
        "pending",
        "upcoming",
        "refunded",
        "unknown"
    ]
    confidence: float
    description: str | None
