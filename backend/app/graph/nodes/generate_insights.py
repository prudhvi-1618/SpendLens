from app.graph.state import SpendState
from services.gemini_service import GeminiService
from langchain_core.messages import SystemMessage, HumanMessage
import json

async def generate_insights(state: SpendState) -> SpendState:
    """
    Generate natural language insights from deterministic analytics.
    """
    total_spending = state.get("total_spending", 0.0)
    category_summary = state.get("category_summary", {})
    merchant_summary = state.get("merchant_summary", {})
    recurring_payments = state.get("recurring_payments", [])
    anomalies = state.get("anomalies", [])
    
    analytics_payload = {
        "total_spending": total_spending,
        "category_summary": category_summary,
        "merchant_summary": merchant_summary,
        "recurring_payments": recurring_payments,
        "anomalies": anomalies
    }
    
    gemini_service = GeminiService()
    llm = gemini_service.get_openrouter_llm()
    
    prompt = f"""
    You are a financial analyst. Based on the following DETERMINISTIC analytics data for a user's recent spending, provide 3 to 5 concise insights.
    DO NOT invent transactions or amounts. Only use the data provided.
    
    Analytics Data:
    {json.dumps(analytics_payload, indent=2)}
    
    Format your response as a valid JSON array of objects with keys 'title' and 'description'.
    Example:
    [
        {{"title": "High food spending", "description": "You spent Rs 5,000 on Swiggy this month."}}
    ]
    """
    
    insights = []
    try:
        res = await llm.ainvoke([HumanMessage(content=prompt)])
        content = res.content.strip()
        # Clean markdown if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        insights = json.loads(content.strip())
    except Exception as e:
        insights = [{"title": "Analysis unavailable", "description": "Could not generate insights at this time."}]
        
    return {
        "insights": insights
    }
