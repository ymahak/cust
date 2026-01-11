"""
Distributed Tracing System
Tracks requests across agents for observability
"""
from typing import Dict, List, Optional
from datetime import datetime, timezone
from uuid import uuid4
import json

# In-memory trace store (in production, use OpenTelemetry/Jaeger)
_traces: Dict[str, Dict] = {}

def create_trace(operation: str, metadata: Optional[Dict] = None) -> str:
    """Create a new trace"""
    trace_id = str(uuid4())
    _traces[trace_id] = {
        "trace_id": trace_id,
        "operation": operation,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "spans": [],
        "metadata": metadata or {},
        "status": "in_progress",
    }
    return trace_id

def add_span(trace_id: str, span_name: str, agent_type: str, duration_ms: float, metadata: Optional[Dict] = None):
    """Add a span to a trace"""
    if trace_id not in _traces:
        return
    
    _traces[trace_id]["spans"].append({
        "span_name": span_name,
        "agent_type": agent_type,
        "duration_ms": duration_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    })

def complete_trace(trace_id: str, status: str = "completed", metadata: Optional[Dict] = None):
    """Complete a trace"""
    if trace_id not in _traces:
        return
    
    _traces[trace_id]["status"] = status
    _traces[trace_id]["end_time"] = datetime.now(timezone.utc).isoformat()
    if metadata:
        _traces[trace_id]["metadata"].update(metadata)

def get_trace(trace_id: str) -> Optional[Dict]:
    """Get a trace by ID"""
    return _traces.get(trace_id)

def get_recent_traces(limit: int = 50) -> List[Dict]:
    """Get recent traces"""
    sorted_traces = sorted(
        _traces.values(),
        key=lambda x: x.get("start_time", ""),
        reverse=True
    )
    return sorted_traces[:limit]

def get_trace_summary() -> Dict:
    """Get trace summary statistics"""
    total = len(_traces)
    completed = sum(1 for t in _traces.values() if t.get("status") == "completed")
    in_progress = sum(1 for t in _traces.values() if t.get("status") == "in_progress")
    
    return {
        "total_traces": total,
        "completed": completed,
        "in_progress": in_progress,
        "success_rate": (completed / total * 100) if total > 0 else 0,
    }
