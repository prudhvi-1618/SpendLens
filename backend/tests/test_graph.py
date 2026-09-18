import pytest

import app.graph.nodes.classify_emails as classify_node
from app.classifiers.email_classifier import EmailClassification, classify_email
from app.graph.nodes.classify_emails import classify_emails
from app.graph.nodes.validate_transactions import validate_transactions
from app.graph.routing import route_financial_emails
from services.gmail_service import GmailService


@pytest.mark.parametrize(
    ("email", "expected", "required_rule"),
    [
        (
            {"subject": "Payment successful: Rs. 1,499", "snippet": "Your card was charged INR 1,499"},
            EmailClassification.COMPLETED_TRANSACTION,
            "payment_successful",
        ),
        (
            {"subject": "Your order has been confirmed", "snippet": "Total: Rs. 450"},
            EmailClassification.COMPLETED_TRANSACTION,
            "purchase_confirmed",
        ),
        (
            {"subject": "Invoice #12345", "snippet": "Amount due INR 2,500"},
            EmailClassification.UPCOMING_PAYMENT,
            "payment_due",
        ),
        (
            {"subject": "Your card was charged INR 2,500", "snippet": "Payment successful"},
            EmailClassification.COMPLETED_TRANSACTION,
            "card_charged",
        ),
        (
            {"subject": "Netflix subscription renewed", "snippet": "Your monthly plan was charged USD 12"},
            EmailClassification.COMPLETED_TRANSACTION,
            "card_charged",
        ),
        (
            {"subject": "Refund of Rs. 499 processed", "snippet": "Amount refunded to your card"},
            EmailClassification.REFUND,
            "refund_processed",
        ),
    ],
)
def test_rule_classifier_financial_categories(email, expected, required_rule):
    result = classify_email(email)

    assert result.classification == expected
    assert required_rule in result.matched_positive_rules
    assert result.score >= 5
    assert result.confidence > 0.5
    assert result.reason


@pytest.mark.parametrize(
    "email",
    [
        {"subject": "Weekly newsletter", "snippet": "Here are the top marketing trends"},
        {"subject": "20% sale this weekend", "snippet": "Use this coupon before Sunday"},
        {"subject": "New blog post", "snippet": "Read our latest article"},
        {"subject": "Community digest", "snippet": "Popular posts from this week"},
        {"subject": "Webinar announcement", "snippet": "Join our event tomorrow"},
    ],
)
def test_rule_classifier_non_financial(email):
    result = classify_email(email)

    assert result.classification == EmailClassification.NON_FINANCIAL
    assert result.score <= 0
    assert result.matched_negative_rules
    assert result.confidence > 0.5
    assert result.reason


def test_rule_classifier_ambiguous():
    result = classify_email({"subject": "Payment options update", "snippet": "Please review the changes"})

    assert result.classification == EmailClassification.UNCERTAIN
    assert result.score > 0
    assert result.confidence == 0.5
    assert result.reason


def test_rule_classifier_false_positive_protection():
    result = classify_email(
        {
            "subject": "Learn how payment transactions work",
            "snippet": "A guide to payment systems, transaction routing, and purchase authorization.",
        }
    )

    assert result.classification == EmailClassification.NON_FINANCIAL
    assert "educational_payment_context" in result.matched_negative_rules
    assert result.score <= 0
    assert result.reason


@pytest.mark.asyncio
async def test_classify_emails_node_uses_batch_local_financial_state():
    state = {
        "current_emails": [
            {
                "message_id": "m1",
                "subject": "Payment successful: Rs. 1,499",
                "snippet": "Your card was charged INR 1,499",
            },
            {
                "message_id": "m2",
                "subject": "Weekly newsletter",
                "snippet": "Here are the top marketing trends",
            },
        ],
        "financial_email_count": 0,
    }

    result = await classify_emails(state)

    assert len(result["current_classifications"]) == 2
    assert result["current_classifications"][0]["message_id"] == "m1"
    assert len(result["current_financial_emails"]) == 1
    assert result["current_financial_emails"][0]["message_id"] == "m1"
    assert result["financial_email_count"] == 1
    assert route_financial_emails(result) == "extract_transactions"


@pytest.mark.asyncio
async def test_classify_emails_routes_uncertain_to_skip_extraction():
    result = await classify_emails(
        {
            "current_emails": [
                {"message_id": "m1", "subject": "Payment options update", "snippet": "Please review the changes"}
            ],
            "financial_email_count": 0,
        }
    )

    assert result["current_classifications"][0]["classification"] == EmailClassification.UNCERTAIN.value
    assert result["current_financial_emails"] == []
    assert route_financial_emails(result) == "__end__"


def test_classifier_node_has_no_llm_dependency():
    assert not hasattr(classify_node, "GeminiService")


def test_gmail_financial_query_includes_search_filter():
    query = GmailService.build_financial_query(months_back=1)

    assert query.startswith("after:")
    assert "(receipt OR invoice" in query
    assert '"payment successful"' in query
    assert query.count(" OR ") > 1


def test_validate_transactions():
    state = {
        "extracted_transactions": [
            {
                "merchant": "Swiggy",
                "amount": 450,
                "currency": "INR",
                "transaction_date": "2023-10-01",
                "confidence": 0.9,
            },
            {
                "merchant": "Uber",
                "amount": -50,
                "currency": "INR",
                "transaction_date": "2023-10-01",
                "confidence": 0.9,
            },
            {
                "merchant": "",
                "amount": 100,
                "currency": "INR",
                "transaction_date": "2023-10-01",
                "confidence": 0.9,
            },
        ]
    }

    res = validate_transactions(state)
    assert len(res["validated_transactions"]) == 1
    assert res["validated_transactions"][0]["merchant"] == "Swiggy"
    assert len(res["errors"]) == 2
