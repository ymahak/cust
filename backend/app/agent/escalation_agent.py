from typing import Dict
try:
    from ..database.mongo import create_escalation as db_create_escalation, get_pending_escalations, resolve_escalation as db_resolve_escalation
except ImportError:
    from database.mongo import create_escalation as db_create_escalation, get_pending_escalations, resolve_escalation as db_resolve_escalation

class EscalationAgent:
    """Handles human-in-the-loop escalations"""
    
    @staticmethod
    async def create_escalation(user_id: str, reason: str, agent_type: str) -> Dict:
        """Create an escalation request"""
        escalation = await db_create_escalation(user_id, reason, agent_type)
        return {
            "status": "escalated",
            "message": "Your request has been escalated to a human agent. Please wait for assistance.",
            "escalation_id": escalation.get("_id")
        }
    
    @staticmethod
    async def get_pending_escalations() -> list:
        """Get all pending escalations for human agents"""
        return await get_pending_escalations()
    
    @staticmethod
    async def resolve_escalation(escalation_id: str, resolution: str) -> Dict:
        """Resolve an escalation"""
        await db_resolve_escalation(escalation_id, resolution)
        return {"status": "resolved", "message": "Escalation resolved successfully"}
