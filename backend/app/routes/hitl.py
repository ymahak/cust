from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.mongo import (
    get_pending_escalations,
    resolve_escalation
)
from app.auth.jwt import verify_token

router = APIRouter(prefix="/hitl", tags=["Human-in-the-Loop"])
security = HTTPBearer()


# ---------------- Schemas ----------------

class EscalationResponse(BaseModel):
    escalation_id: str
    response: str
    notes: str | None = None


# ---------------- Helpers ----------------

def require_agent_or_admin(credentials: HTTPAuthorizationCredentials):
    payload = verify_token(credentials.credentials)
    if payload["role"] not in ["agent", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent or Admin access required"
        )
    return payload


# ---------------- Routes ----------------

@router.get("/escalations/pending")
async def get_pending(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    require_agent_or_admin(credentials)
    return await get_pending_escalations()


@router.post("/escalations/resolve")
async def resolve(
    data: EscalationResponse,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    require_agent_or_admin(credentials)

    await resolve_escalation(
        escalation_id=data.escalation_id,
        human_response=data.response,
        notes=data.notes
    )

    return {
        "status": "resolved",
        "message": "Escalation resolved successfully"
    }
