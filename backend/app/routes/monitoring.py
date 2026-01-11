"""
Monitoring and Analytics Routes
Provides metrics, traces, and system health information
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

try:
    from ..monitoring.metrics import get_metrics, get_escalation_stats
    from ..monitoring.tracer import get_recent_traces, get_trace_summary, get_trace
    from ..auth.jwt import verify_token
except ImportError:
    from monitoring.metrics import get_metrics, get_escalation_stats
    from monitoring.tracer import get_recent_traces, get_trace_summary, get_trace
    from auth.jwt import verify_token

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
security = HTTPBearer()

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

@router.get("/metrics")
async def get_metrics_endpoint(current_user: Dict = Depends(get_admin_user)):
    """Get system metrics and agent performance"""
    metrics = get_metrics()
    escalation_stats = get_escalation_stats()
    
    return {
        "metrics": metrics,
        "escalation_stats": escalation_stats,
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    }

@router.get("/traces")
async def get_traces_endpoint(
    limit: int = 50,
    current_user: Dict = Depends(get_admin_user)
):
    """Get recent traces"""
    traces = get_recent_traces(limit=limit)
    summary = get_trace_summary()
    
    return {
        "traces": traces,
        "summary": summary
    }

@router.get("/traces/{trace_id}")
async def get_trace_endpoint(
    trace_id: str,
    current_user: Dict = Depends(get_admin_user)
):
    """Get a specific trace by ID"""
    trace = get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace

@router.get("/dashboard")
async def get_dashboard_data(current_user: Dict = Depends(get_admin_user)):
    """Get comprehensive dashboard data"""
    metrics = get_metrics()
    escalation_stats = get_escalation_stats()
    trace_summary = get_trace_summary()
    recent_traces = get_recent_traces(limit=10)
    
    return {
        "agent_performance": metrics.get("agent_performance", {}),
        "intent_distribution": metrics.get("intent_distribution", {}),
        "escalation_stats": escalation_stats,
        "trace_summary": trace_summary,
        "recent_traces": recent_traces,
        "total_calls": metrics.get("total_calls", 0),
        "total_escalations": metrics.get("total_escalations", 0),
    }
