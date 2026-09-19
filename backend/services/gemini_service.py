import os
import json
import logging
import warnings
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

# Suppress annoying Pydantic/Google GenAI schema warnings
warnings.filterwarnings("ignore", message="Key 'title' is not supported in schema, ignoring")

class GeminiService:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-3.6-flash")

    async def extract_batch(self, emails: list[dict]) -> list[dict]:
        if not emails:
            return []

        prompt = "Extract financial transaction details from the following emails. " \
                 "Return ONLY a JSON array of objects, one per email, in the exact same order. " \
                 "Each object must follow this schema:\n" \
                 "{\n" \
                 "  \"merchant\": \"cleaned company name\",\n" \
                 "  \"amount\": <float, no currency symbol>,\n" \
                 "  \"currency\": \"INR or correct 3-letter code\",\n" \
                 "  \"category\": \"one of [travel, food, subscription, utilities, shopping, entertainment, healthcare, other]\",\n" \
                 "  \"date\": \"YYYY-MM-DD\",\n" \
                 "  \"confidence\": <0.0 to 1.0>\n" \
                 "}\n" \
                 "If an email is not a financial transaction, its object MUST be exactly: {\"confidence\": 0}\n\n"

        for i, email in enumerate(emails):
            prompt += f"[{i}] Subject: {email.get('subject', '')}\nSnippet: {email.get('snippet', '')}\n\n"

        default_error_return = [{"confidence": 0}] * len(emails)

        try:
            response = await self.model.generate_content_async(prompt)
            text = response.text.strip()
            
            # Strip markdown fences if present
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            text = text.strip()
            
            results = json.loads(text)
            
            if not isinstance(results, list):
                logger.error("Gemini response is not a JSON array.")
                return default_error_return
            
            # Pad or truncate to match length
            if len(results) < len(emails):
                results.extend([{"confidence": 0}] * (len(emails) - len(results)))
            elif len(results) > len(emails):
                results = results[:len(emails)]
                
            return results
            
        except Exception as e:
            logger.error(f"Error extracting batch with Gemini: {e}")
            return default_error_return

    def get_langchain_llm(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            temperature=0.2
        )

    def get_openrouter_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model="inclusionai/ling-3.0-flash-fin:free",
            api_key=os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPEN_ROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2
        )
