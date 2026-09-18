import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from langchain.prompts import PromptTemplate

from models import Transaction

logger = logging.getLogger(__name__)

class SpendProfiler:
    def __init__(self, llm):
        self.llm = llm

    async def build_profile(self, user_id: str, db: AsyncSession) -> dict:
        ninety_days_ago = datetime.utcnow().date() - timedelta(days=90)
        
        try:
            # 1. Total Spend
            total_result = await db.execute(
                select(func.sum(Transaction.amount))
                .where(Transaction.user_id == user_id, Transaction.date >= ninety_days_ago)
            )
            total_spend = float(total_result.scalar() or 0)
            
            # 2. By Category
            category_result = await db.execute(
                select(Transaction.category, func.sum(Transaction.amount))
                .where(Transaction.user_id == user_id, Transaction.date >= ninety_days_ago, Transaction.category != None)
                .group_by(Transaction.category)
                .order_by(func.sum(Transaction.amount).desc())
            )
            by_category = {row[0]: float(row[1]) for row in category_result.all()}
            
            # 3. By Merchant (Top 10)
            merchant_result = await db.execute(
                select(Transaction.merchant, func.sum(Transaction.amount))
                .where(Transaction.user_id == user_id, Transaction.date >= ninety_days_ago, Transaction.merchant != None)
                .group_by(Transaction.merchant)
                .order_by(func.sum(Transaction.amount).desc())
                .limit(10)
            )
            by_merchant = {row[0]: float(row[1]) for row in merchant_result.all()}
            
            # 4. Monthly Totals
            month_key = func.to_char(Transaction.date, 'YYYY-MM')
            monthly_result = await db.execute(
                select(month_key, func.sum(Transaction.amount))
                .where(Transaction.user_id == user_id, Transaction.date >= ninety_days_ago, Transaction.date != None)
                .group_by(month_key)
                .order_by(month_key)
            )
            monthly_totals = {row[0]: float(row[1]) for row in monthly_result.all()}
            
            # 5. Recurring Merchants
            recurring_result = await db.execute(
                select(Transaction.merchant)
                .where(Transaction.user_id == user_id, Transaction.merchant != None)
                .group_by(Transaction.merchant)
                .having(func.count() >= 2)
            )
            recurring = [row[0] for row in recurring_result.all()]
            
            # Build plain-text spend data block
            spend_data_text = f"Total spend (90 days): ₹{total_spend:.2f}\n"
            spend_data_text += f"By category: {by_category}\n"
            spend_data_text += f"Top merchants: {by_merchant}\n"
            spend_data_text += f"Monthly: {monthly_totals}\n"
            spend_data_text += f"Recurring merchants: {recurring}"
            
            # Use LangChain LLMChain
            template = """You are a personal finance analyst.
            Based on this spending data, write a 4-6 sentence plain-English summary.
            Mention the highest-spend category, the single biggest merchant, and one
            specific actionable observation the user can act on. Use INR amounts.

            Data:
            {spend_data}

            Summary:"""
            
            prompt = PromptTemplate(template=template, input_variables=["spend_data"])
            chain = prompt | self.llm
            response = await chain.ainvoke({"spend_data": spend_data_text})
            summary_text = response.content if hasattr(response, "content") else str(response)
            
            return {
                "total_spend": total_spend,
                "by_category": by_category,
                "by_merchant": by_merchant,
                "monthly_totals": monthly_totals,
                "recurring": recurring,
                "summary_text": summary_text,
                "period_days": 90
            }
            
        except Exception as e:
            logger.error(f"Error building profile: {e}")
            return {
                "total_spend": 0,
                "by_category": {},
                "by_merchant": {},
                "monthly_totals": {},
                "recurring": [],
                "summary_text": "Could not generate profile due to an error.",
                "period_days": 90
            }
