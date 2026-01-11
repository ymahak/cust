from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict, Optional

load_dotenv()

def get_openai_client():
    """Get OpenAI client with API key"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)

INTENT_PROMPT = """You are an intent classification agent. Analyze the user's message and classify it into one of these categories:
- greeting: Simple greetings or hello
- question: General questions about products/services
- complaint: Issues or problems
- refund: Refund requests
- technical: Technical support needed
- billing: Billing or payment issues
- other: Anything else

Respond with ONLY the category name, nothing else."""

def classify_intent(user_message: str) -> str:
    """Classify user intent"""
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        intent = response.choices[0].message.content.strip().lower()
        
        # Validate intent
        valid_intents = ["greeting", "question", "complaint", "refund", "technical", "billing", "other"]
        if intent not in valid_intents:
            intent = "other"
        
        return intent
    except Exception as e:
        print(f"Error in intent classification: {e}")
        return "other"
