from typing import Dict, List

from app.database.mongo import (
    create_escalation as db_create_escalation,
    get_pending_escalations,
    resolve_escalation as db_resolve_escalation
)

# ------------------------------------------------------------------
# Escalation Decision Logic (USED BY chat.py)
# ------------------------------------------------------------------

def should_escalate(ai_response: str, intent: str) -> bool:
    """
    Decide whether an AI response should be escalated to a human.

    Escalation rules:
    - Sensitive intents
    - Low-confidence or uncertain AI language
    """

    sensitive_intents = [
        "complaint",
        "refund",
        "billing",
        "technical"
    ]

    uncertainty_phrases = [
        "not sure",
        "cannot help",
        "unable to",
        "i don't know",
        "might be wrong",
    ]

    if intent.lower() in sensitive_intents:
        return True

    response_lower = ai_response.lower()
    for phrase in uncertainty_phrases:
        if phrase in response_lower:
            return True

    return False


# ------------------------------------------------------------------
# Escalation Agent (HITL lifecycle)
# ------------------------------------------------------------------

class EscalationAgent:
    """Handles human-in-the-loop escalation lifecycle"""

    @staticmethod
    async def create_escalation(
        user_message: str,
        ai_response: str,
        intent: str,
        reason: str
    ) -> Dict:
        await db_create_escalation(
            user_message=user_message,
            ai_response=ai_response,
            intent=intent,
            reason=reason
        )
        return {
            "status": "escalated",
            "message": "Your request has been escalated to a human agent."
        }

    @staticmethod
    async def get_pending_escalations() -> List[Dict]:
        return await get_pending_escalations()

    @staticmethod
    async def resolve_escalation(
        escalation_id: str,
        human_response: str,
        notes: str | None = None
    ) -> Dict:
        await db_resolve_escalation(
            escalation_id=escalation_id,
            human_response=human_response,
            notes=notes
        )
        return {
            "status": "resolved",
            "message": "Escalation resolved successfully"
        }
