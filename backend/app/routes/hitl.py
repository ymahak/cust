"""
HITL (Human-in-the-Loop) Routes
Admin/Agent dashboard for reviewing and managing escalations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime, timezone

try:
    from ..database.mongo import (
        connect_db,
        get_pending_escalations,
        resolve_escalation,
        get_escalation,
        update_escalation_response,
        save_human_feedback,
    )
    from ..auth.jwt import verify_token
    from ..monitoring.logger import setup_logger
except ImportError:
    from database.mongo import (
        connect_db,
        get_pending_escalations,
        resolve_escalation,
        get_escalation,
        update_escalation_response,
        save_human_feedback,
    )
    from auth.jwt import verify_token
    from monitoring.logger import setup_logger

router = APIRouter(prefix="/hitl", tags=["hitl"])
security = HTTPBearer()
logger = setup_logger()

# ===============================
# Schemas
# ===============================

class EscalationResponse(BaseModel):
    response: str
    notes: Optional[str] = None

class EditResponse(BaseModel):
    original_response: str
    edited_response: str
    reason: str

class FeedbackResponse(BaseModel):
    escalation_id: str
    rating: int  # 1-5
    feedback: Optional[str] = None

# ===============================
# Auth Helper
# ===============================

async def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Require admin or agent role"""
    try:
        payload = verify_token(credentials.credentials)
        role = payload.get("role")
        if role not in ["admin", "agent"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin or agent role required"
            )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# ===============================
# HITL Endpoints
# ===============================

@router.get("/escalations/pending")
async def list_pending_escalations(
    current_user: Dict = Depends(get_admin_user)
):
    """Get all pending escalations for review"""
    await connect_db()
    escalations = await get_pending_escalations()
    return {"escalations": escalations, "count": len(escalations)}

@router.get("/escalations/{escalation_id}")
async def get_escalation_details(
    escalation_id: str,
    current_user: Dict = Depends(get_admin_user)
):
    """Get detailed information about an escalation"""
    await connect_db()
    escalation = await get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return escalation

@router.post("/escalations/{escalation_id}/approve")
async def approve_escalation(
    escalation_id: str,
    response: EscalationResponse,
    current_user: Dict = Depends(get_admin_user)
):
    """Approve and send response to user"""
    await connect_db()
    
    # Get escalation details
    escalation = await get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    # Update escalation with human response
    await update_escalation_response(
        escalation_id=escalation_id,
        response=response.response,
        reviewed_by=current_user["username"],
        notes=response.notes,
        status="approved"
    )
    
    # Save human feedback
    await save_human_feedback(
        escalation_id=escalation_id,
        reviewer=current_user["username"],
        action="approved",
        response=response.response,
        notes=response.notes
    )
    
    logger.info(f"Escalation {escalation_id} approved by {current_user['username']}")
    
    return {
        "status": "approved",
        "message": "Response approved and sent to user",
        "escalation_id": escalation_id
    }

@router.post("/escalations/{escalation_id}/reject")
async def reject_escalation(
    escalation_id: str,
    response: EscalationResponse,
    current_user: Dict = Depends(get_admin_user)
):
    """Reject escalation and provide alternative response"""
    await connect_db()
    
    escalation = await get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    await update_escalation_response(
        escalation_id=escalation_id,
        response=response.response,
        reviewed_by=current_user["username"],
        notes=response.notes,
        status="rejected"
    )
    
    await save_human_feedback(
        escalation_id=escalation_id,
        reviewer=current_user["username"],
        action="rejected",
        response=response.response,
        notes=response.notes
    )
    
    logger.info(f"Escalation {escalation_id} rejected by {current_user['username']}")
    
    return {
        "status": "rejected",
        "message": "Escalation rejected with new response",
        "escalation_id": escalation_id
    }

@router.post("/escalations/{escalation_id}/edit")
async def edit_response(
    escalation_id: str,
    edit: EditResponse,
    current_user: Dict = Depends(get_admin_user)
):
    """Edit an AI-generated response"""
    await connect_db()
    
    escalation = await get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    await update_escalation_response(
        escalation_id=escalation_id,
        response=edit.edited_response,
        reviewed_by=current_user["username"],
        notes=f"Edited: {edit.reason}",
        status="edited"
    )
    
    await save_human_feedback(
        escalation_id=escalation_id,
        reviewer=current_user["username"],
        action="edited",
        response=edit.edited_response,
        original_response=edit.original_response,
        notes=edit.reason
    )
    
    logger.info(f"Escalation {escalation_id} edited by {current_user['username']}")
    
    return {
        "status": "edited",
        "message": "Response edited successfully",
        "escalation_id": escalation_id
    }

@router.get("/stats")
async def get_hitl_stats(current_user: Dict = Depends(get_admin_user)):
    """Get HITL statistics"""
    await connect_db()
    
    # This would query the database for stats
    # For now, return basic structure
    return {
        "pending_count": len(await get_pending_escalations()),
        "reviewed_today": 0,  # Would query DB
        "avg_review_time_minutes": 0,  # Would calculate from DB
    }
