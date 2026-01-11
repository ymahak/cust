from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Dict

try:
    from ..agent.intent_agent import classify_intent
    from ..agent.support_agent import generate_response
    from ..agent.escalation_agent import EscalationAgent
    from ..security.guardrails import check_guardrails
    from ..monitoring.logger import setup_logger
    from ..database.mongo import (
        connect_db,
        save_message,
        get_conversation_history,
    )
    from ..auth.jwt import verify_token
except ImportError:
    from agent.intent_agent import classify_intent
    from agent.support_agent import generate_response
    from agent.escalation_agent import EscalationAgent
    from security.guardrails import check_guardrails
    from monitoring.logger import setup_logger
    from database.mongo import (
        connect_db,
        save_message,
        get_conversation_history,
    )
    from auth.jwt import verify_token

router = APIRouter()
logger = setup_logger()

# ===============================
# Schemas
# ===============================

class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    intent: str
    agent_type: str
    escalated: bool
    timestamp: str


# ===============================
# AUTH (used only for admin routes)
# ===============================

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    try:
        payload = verify_token(credentials.credentials)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# ===============================
# PUBLIC CHAT ENDPOINT (NO JWT)
# ===============================

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Public AI chat endpoint
    - Multi-agent system
    - Guardrails
    - HITL escalation
    - MongoDB logging
    """

    user_id = "guest_user"

    # Ensure DB connection
    try:
        await connect_db()
    except Exception as e:
        logger.error(f"DB connection issue: {e}")

    # ---------------------------
    # Guardrails
    # ---------------------------
    guardrail = check_guardrails(chat_message.message)
    if not guardrail["allowed"]:
        return ChatResponse(
            response="This request violates usage policies.",
            intent="blocked",
            agent_type="guardrail",
            escalated=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # ---------------------------
    # Intent Agent
    # ---------------------------
    try:
        intent = classify_intent(chat_message.message)
    except Exception as e:
        logger.error(f"Intent error: {e}")
        intent = "unknown"

    # ---------------------------
    # Conversation History
    # ---------------------------
    try:
        history = await get_conversation_history(user_id, limit=10)
    except Exception:
        history = []

    # ---------------------------
    # Support Agent
    # ---------------------------
    try:
        agent_result = generate_response(
            chat_message.message,
            intent,
            history,
        )

        response_text = agent_result.get("response")
        needs_escalation = agent_result.get("needs_escalation", False)
        agent_type = agent_result.get("agent_type", "support_agent")

    except Exception as e:
        logger.error(f"Support agent error: {e}")
        response_text = "I'm facing some technical issues. Please try again later."
        needs_escalation = True
        agent_type = "error"

    # ---------------------------
    # HITL Escalation Agent
    # ---------------------------
    if needs_escalation:
        try:
            escalation = await EscalationAgent.create_escalation(
                user_id,
                f"Support agent unable to handle: {intent}",
                agent_type,
            )
            response_text = escalation.get(
                "message",
                "Your request has been escalated to human support.",
            )
            agent_type = "escalation_agent"
        except Exception as e:
            logger.error(f"Escalation error: {e}")

    # ---------------------------
    # Save Conversation
    # ---------------------------
    try:
        await save_message(
            user_id=user_id,
            message=chat_message.message,
            response=response_text,
            agent_type=agent_type,
            metadata={
                "intent": intent,
                "escalated": needs_escalation,
            },
        )
    except Exception as e:
        logger.error(f"Save error: {e}")

    # ---------------------------
    # Final Response
    # ---------------------------
    return ChatResponse(
        response=response_text,
        intent=intent,
        agent_type=agent_type,
        escalated=needs_escalation,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# ===============================
# PROTECTED ROUTES (JWT REQUIRED)
# ===============================

@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user["username"]
    await connect_db()
    history = await get_conversation_history(user_id)
    return {"history": history}


@router.get("/escalations")
async def get_escalations(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return {"escalations": await EscalationAgent.get_pending_escalations()}
