from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

def get_openai_client():
    """Get OpenAI client with API key"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)

SUPPORT_PROMPT = """You are a helpful customer support agent. Your role is to:
1. Provide friendly, professional assistance
2. Answer questions accurately
3. Help resolve issues
4. Escalate to human agents when needed (mention "ESCALATE" if you cannot help)

Keep responses concise, helpful, and empathetic. If the issue requires human intervention, end your response with "ESCALATE"."""

def generate_response(
    user_message: str,
    intent: str,
    conversation_history: Optional[List[Dict]] = None
) -> Dict[str, any]:
    """Generate support response"""
    try:
        # Build context from history
        context = ""
        if conversation_history:
            recent_history = conversation_history[-5:]  # Last 5 messages
            context = "\n".join([
                f"User: {msg.get('message', '')}\nAgent: {msg.get('response', '')}"
                for msg in recent_history
            ])
        
        messages = [
            {"role": "system", "content": SUPPORT_PROMPT},
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Previous conversation:\n{context}"})
        
        messages.append({
            "role": "system",
            "content": f"User intent: {intent}"
        })
        messages.append({"role": "user", "content": user_message})
        
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Check if escalation is needed
        needs_escalation = "ESCALATE" in response_text.upper()
        if needs_escalation:
            response_text = response_text.replace("ESCALATE", "").strip()
        
        return {
            "response": response_text,
            "needs_escalation": needs_escalation,
            "agent_type": "support_agent"
        }
    except Exception as e:
        print(f"Error in support agent: {e}")
        # Fallback to a helpful message if OpenAI fails
        return {
            "response": f"I understand you're asking about: {user_message}. I'd be happy to help! Could you provide more details?",
            "needs_escalation": False,
            "agent_type": "support_agent"
        }
