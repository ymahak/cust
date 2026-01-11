from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

# ---------- OpenAI Client ----------
def get_openai_client():
    """Create and return OpenAI client"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)


# ---------- System Prompt ----------
SUPPORT_PROMPT = """
You are a helpful customer support agent.

Your responsibilities:
1. Provide friendly and professional assistance
2. Answer user questions accurately
3. Help resolve customer issues
4. Escalate to a human agent when the issue is complex or uncertain

IMPORTANT:
- If escalation is needed, include the word "ESCALATE" at the end of your response.
- Keep responses concise, empathetic, and clear.
"""


# ---------- Main Response Generator ----------
def generate_response(
    user_message: str,
    intent: str,
    conversation_history: Optional[List[Dict]] = None
) -> Dict[str, any]:
    """
    Generate an AI support response.

    Returns:
    {
        "response": str,
        "needs_escalation": bool,
        "agent_type": "support_agent"
    }
    """
    try:
        messages = [
            {"role": "system", "content": SUPPORT_PROMPT},
            {"role": "system", "content": f"User intent: {intent}"},
        ]

        # Add limited conversation history (if any)
        if conversation_history:
            history_context = "\n".join(
                f"User: {h.get('message', '')}\nAgent: {h.get('response', '')}"
                for h in conversation_history[-5:]
            )
            messages.append({
                "role": "system",
                "content": f"Previous conversation:\n{history_context}"
            })

        # User message
        messages.append({
            "role": "user",
            "content": user_message
        })

        client = get_openai_client()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )

        response_text = completion.choices[0].message.content.strip()

        # Detect escalation signal
        needs_escalation = "ESCALATE" in response_text.upper()
        if needs_escalation:
            response_text = response_text.replace("ESCALATE", "").strip()

        return {
            "response": response_text,
            "needs_escalation": needs_escalation,
            "agent_type": "support_agent"
        }

    except Exception as e:
        print(f"[SupportAgent Error] {e}")

        # Safe fallback
        return {
            "response": (
                "I'm here to help, but I need a bit more information to assist you properly. "
                "Could you please provide more details?"
            ),
            "needs_escalation": False,
            "agent_type": "support_agent"
        }
