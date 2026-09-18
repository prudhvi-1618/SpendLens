from app.graph.state import SpendState

def route_financial_emails(state: SpendState) -> str:
    """
    Route based on the current batch classification results.

    Uncertain emails are skipped by classify_emails, so only decisive financial
    categories reach extraction.
    """
    if len(state.get("current_financial_emails", [])) > 0:
        return "extract_transactions"
    
    # Phase 2 will route to pagination_check instead of END
    return "__end__"
