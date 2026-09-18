from langgraph.graph import StateGraph, START, END
from app.graph.state import SpendState
from app.graph.nodes.fetch_emails import fetch_emails
from app.graph.nodes.classify_emails import classify_emails
from app.graph.nodes.extract_transactions import extract_transactions
from app.graph.nodes.validate_transactions import validate_transactions
# Phase 2+ nodes will be added here
# from backend.app.graph.nodes.deduplicate_transactions import deduplicate_transactions
# from backend.app.graph.nodes.persist_transactions import persist_transactions
# from backend.app.graph.nodes.analyze_spending import analyze_spending
# from backend.app.graph.nodes.detect_recurring import detect_recurring
# from backend.app.graph.nodes.detect_anomalies import detect_anomalies
# from backend.app.graph.nodes.generate_insights import generate_insights

from app.graph.routing import route_financial_emails

# Phase 1 graph setup
graph = StateGraph(SpendState)

graph.add_node("fetch_emails", fetch_emails)
graph.add_node("classify_emails", classify_emails)
graph.add_node("extract_transactions", extract_transactions)
graph.add_node("validate_transactions", validate_transactions)

graph.add_edge(START, "fetch_emails")
graph.add_edge("fetch_emails", "classify_emails")
graph.add_conditional_edges("classify_emails", route_financial_emails)
graph.add_edge("extract_transactions", "validate_transactions")
graph.add_edge("validate_transactions", END) # Temporary for Phase 1

orchestrator = graph.compile()
