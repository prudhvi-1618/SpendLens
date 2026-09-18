from enum import Enum
import re
from typing import Any

from pydantic import BaseModel

from app.classifiers.rules import (
    FINANCIAL_THRESHOLD,
    NEGATIVE_RULES,
    NON_FINANCIAL_THRESHOLD,
    POSITIVE_RULES,
    SENDER_RULES,
    Rule,
)


class EmailClassification(str, Enum):
    COMPLETED_TRANSACTION = "completed_transaction"
    UPCOMING_PAYMENT = "upcoming_payment"
    FINANCIAL_DOCUMENT = "financial_document"
    REFUND = "refund"
    NON_FINANCIAL = "non_financial"
    UNCERTAIN = "uncertain"


class ClassificationResult(BaseModel):
    classification: EmailClassification
    score: int
    confidence: float
    matched_positive_rules: list[str]
    matched_negative_rules: list[str]
    reason: str

    @property
    def is_financial(self) -> bool:
        return self.classification in {
            EmailClassification.COMPLETED_TRANSACTION,
            EmailClassification.UPCOMING_PAYMENT,
            EmailClassification.FINANCIAL_DOCUMENT,
            EmailClassification.REFUND,
        }


def normalize_text(*parts: Any) -> str:
    text = " ".join(str(part or "") for part in parts)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _matching_rules(rules: tuple[Rule, ...], text: str) -> list[Rule]:
    return [rule for rule in rules if re.search(rule.pattern, text, re.IGNORECASE)]


def _confidence(score: int, classification: EmailClassification) -> float:
    if classification == EmailClassification.UNCERTAIN:
        return 0.5
    if classification == EmailClassification.NON_FINANCIAL:
        return round(min(0.95, 0.55 + (abs(score) * 0.08)), 2)
    return round(min(0.99, 0.55 + (score * 0.06)), 2)


def _choose_financial_classification(matches: list[Rule]) -> EmailClassification:
    kinds = {rule.kind for rule in matches}

    if "refund" in kinds:
        return EmailClassification.REFUND
    if "upcoming_payment" in kinds:
        return EmailClassification.UPCOMING_PAYMENT
    if "completed_transaction" in kinds:
        return EmailClassification.COMPLETED_TRANSACTION
    if "financial_document" in kinds:
        return EmailClassification.FINANCIAL_DOCUMENT
    if "subscription" in kinds:
        return EmailClassification.FINANCIAL_DOCUMENT
    return EmailClassification.FINANCIAL_DOCUMENT


def _reason(
    classification: EmailClassification,
    positive_matches: list[Rule],
    negative_matches: list[Rule],
) -> str:
    positive = ", ".join(rule.name for rule in positive_matches[:3])
    negative = ", ".join(rule.name for rule in negative_matches[:3])

    if classification == EmailClassification.NON_FINANCIAL:
        if negative:
            return f"Classified as non-financial because negative signals matched: {negative}."
        return "Classified as non-financial because financial evidence was too weak."

    if classification == EmailClassification.UNCERTAIN:
        if positive and negative:
            return f"Uncertain because financial signals ({positive}) were offset by non-financial signals ({negative})."
        if positive:
            return f"Uncertain because only weak financial signals matched: {positive}."
        return "Uncertain because no decisive financial signals matched."

    if negative:
        return f"Matched financial signals ({positive}) despite non-financial signals ({negative})."
    return f"Matched financial signals: {positive}."


def classify_email(email: dict[str, Any]) -> ClassificationResult:
    subject = email.get("subject", "")
    sender = email.get("sender", "") or email.get("from", "")
    sender_email = email.get("sender_email", "")
    snippet = email.get("snippet", "")
    body = email.get("body", "")

    text = normalize_text(subject, snippet, body)
    sender_text = normalize_text(sender, sender_email)

    positive_matches = _matching_rules(POSITIVE_RULES, text)
    sender_matches = _matching_rules(SENDER_RULES, sender_text)
    negative_matches = _matching_rules(NEGATIVE_RULES, text)

    all_positive_matches = positive_matches + sender_matches
    score = sum(rule.weight for rule in all_positive_matches) + sum(rule.weight for rule in negative_matches)

    has_contextual_finance = any(
        rule.kind
        in {
            "completed_transaction",
            "upcoming_payment",
            "financial_document",
            "refund",
            "subscription",
            "currency_amount",
        }
        for rule in all_positive_matches
    )

    if score >= FINANCIAL_THRESHOLD and has_contextual_finance:
        classification = _choose_financial_classification(all_positive_matches)
    elif score <= NON_FINANCIAL_THRESHOLD:
        classification = EmailClassification.NON_FINANCIAL
    else:
        classification = EmailClassification.UNCERTAIN

    return ClassificationResult(
        classification=classification,
        score=score,
        confidence=_confidence(score, classification),
        matched_positive_rules=[rule.name for rule in all_positive_matches],
        matched_negative_rules=[rule.name for rule in negative_matches],
        reason=_reason(classification, all_positive_matches, negative_matches),
    )
