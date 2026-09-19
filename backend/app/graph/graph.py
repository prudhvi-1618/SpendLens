from langgraph.graph import StateGraph, START, END
from app.graph.state import SpendState
from app.graph.nodes.fetch_emails import fetch_emails
from app.graph.nodes.classify_emails import classify_emails
from app.graph.nodes.extract_transactions import extract_transactions
from app.graph.nodes.validate_transactions import validate_transactions
# Phase 2+ nodes will be added here
from app.graph.nodes.deduplicate_transactions import deduplicate_transactions
from app.graph.nodes.persist_transactions import persist_transactions
from app.graph.nodes.analyze_spending import analyze_spending
from app.graph.nodes.detect_recurring import detect_recurring
from app.graph.nodes.detect_anomalies import detect_anomalies
from app.graph.nodes.generate_insights import generate_insights

from app.graph.routing import route_financial_emails

# Phase 1 graph setup
graph = StateGraph(SpendState)

graph.add_node("fetch_emails", fetch_emails)
graph.add_node("classify_emails", classify_emails)
graph.add_node("extract_transactions", extract_transactions)
graph.add_node("validate_transactions", validate_transactions)
graph.add_node("deduplicate_transactions", deduplicate_transactions)
graph.add_node("persist_transactions", persist_transactions)
graph.add_node("analyze_spending", analyze_spending)
graph.add_node("detect_recurring", detect_recurring)
graph.add_node("detect_anomalies", detect_anomalies)
graph.add_node("generate_insights", generate_insights)

graph.add_edge(START, "fetch_emails")
graph.add_edge("fetch_emails", "classify_emails")
graph.add_conditional_edges("classify_emails", route_financial_emails)
graph.add_edge("extract_transactions", "validate_transactions")
graph.add_edge("validate_transactions", "deduplicate_transactions")
graph.add_edge("deduplicate_transactions", "persist_transactions")
graph.add_edge("persist_transactions", "analyze_spending")
graph.add_edge("analyze_spending", "detect_recurring")
graph.add_edge("detect_recurring", "detect_anomalies")
graph.add_edge("detect_anomalies", "generate_insights")
graph.add_edge("generate_insights", END)

orchestrator = graph.compile()
