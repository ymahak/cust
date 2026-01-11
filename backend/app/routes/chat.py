from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

from app.agents.intent_agent import classify_intent
from app.agents.support_agent import generate_response
from app.agents.escalation_agent import should_escalate
from app.security.guardrails import check_guardrails
from app.database.mongo import save_message, create_escalation
from app.monitoring.logger import log_event

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/")
async def chat(data: ChatRequest):
    message = data.message

    # 1. Guardrails
    guardrail_result = check_guardrails(message)
    if not guardrail_result["allowed"]:
        raise HTTPException(
            status_code=400,
            detail=guardrail_result["reason"]
        )

    # 2. Intent classification
    intent = classify_intent(message)

    # 3. Generate response
    result = generate_response(
        user_message=message,
        intent=intent
    )

    ai_response = result["response"]
    needs_escalation = result["needs_escalation"]

    # 4. HITL escalation
    escalated = False
    if needs_escalation or should_escalate(ai_response, intent):
        await create_escalation(
            user_message=message,
            ai_response=ai_response,
            intent=intent,
            reason="Low confidence or sensitive intent"
        )
        escalated = True

    # 5. Save message
    await save_message(
        message=message,
        response=ai_response,
        intent=intent,
        escalated=escalated,
        timestamp=datetime.utcnow()
    )

    # 6. Log
    log_event("CHAT_REQUEST", {
        "intent": intent,
        "escalated": escalated
    })

    return {
        "response": ai_response,
        "intent": intent,
        "escalated": escalated,
        "timestamp": datetime.utcnow()
    }
