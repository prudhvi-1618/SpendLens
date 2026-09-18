import logging
from app.classifiers.email_classifier import classify_email
from app.graph.state import SpendState

logger = logging.getLogger(__name__)


async def classify_emails(state: SpendState) -> SpendState:
    """
    Deterministically classify the current email batch.

    UNCERTAIN emails are intentionally skipped for extraction. The extractor
    should only receive emails with decisive financial evidence.
    """
    logger.info("--- NODE: classify_emails START ---")
    print("--- NODE: classify_emails START ---")
    current_emails = state.get("current_emails", [])
    current_classifications = []
    current_financial_emails = []

    for email in current_emails:
        result = classify_email(email)
        result_dict = result.model_dump(mode="json")
        result_dict["message_id"] = email.get("message_id")
        current_classifications.append(result_dict)

        if result.is_financial:
            email_with_classification = {
                **email,
                "classification": result.classification.value,
                "classification_score": result.score,
                "classification_confidence": result.confidence,
            }
            current_financial_emails.append(email_with_classification)
    
    logger.info(f"--- NODE: classify_emails END (Found {len(current_financial_emails)} financial) ---")
    print(f"--- NODE: classify_emails END (Found {len(current_financial_emails)} financial) ---")
    return {
        "current_classifications": current_classifications,
        "current_financial_emails": current_financial_emails,
        "financial_emails": current_financial_emails,
        "financial_email_count": state.get("financial_email_count", 0) + len(current_financial_emails),
    }
