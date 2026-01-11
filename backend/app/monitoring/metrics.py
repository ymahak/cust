"""
Metrics and Performance Tracking System
Tracks agent performance, latency, escalation rates, and more
"""
from typing import Dict, List
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import time
try:
    from ..database.mongo import connect_db
except ImportError:
    from database.mongo import connect_db

# In-memory metrics store (in production, use Redis or time-series DB)
_metrics = {
    "agent_calls": defaultdict(int),
    "agent_latency": defaultdict(list),
    "escalations": defaultdict(int),
    "intent_distribution": defaultdict(int),
    "errors": defaultdict(int),
}

def record_agent_call(agent_type: str, latency_ms: float):
    """Record an agent call with latency"""
    _metrics["agent_calls"][agent_type] += 1
    _metrics["agent_latency"][agent_type].append(latency_ms)
    # Keep only last 1000 latency measurements
    if len(_metrics["agent_latency"][agent_type]) > 1000:
        _metrics["agent_latency"][agent_type] = _metrics["agent_latency"][agent_type][-1000:]

def record_intent(intent: str):
    """Record intent classification"""
    _metrics["intent_distribution"][intent] += 1

def record_escalation(agent_type: str):
    """Record an escalation"""
    _metrics["escalations"][agent_type] += 1

def record_error(agent_type: str, error_type: str):
    """Record an error"""
    _metrics["errors"][f"{agent_type}_{error_type}"] += 1

def get_metrics() -> Dict:
    """Get all metrics"""
    agent_stats = {}
    
    for agent_type in _metrics["agent_calls"]:
        latencies = _metrics["agent_latency"][agent_type]
        agent_stats[agent_type] = {
            "total_calls": _metrics["agent_calls"][agent_type],
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "escalations": _metrics["escalations"][agent_type],
            "escalation_rate": (
                _metrics["escalations"][agent_type] / _metrics["agent_calls"][agent_type]
                if _metrics["agent_calls"][agent_type] > 0
                else 0
            ),
        }
    
    return {
        "agent_performance": agent_stats,
        "intent_distribution": dict(_metrics["intent_distribution"]),
        "errors": dict(_metrics["errors"]),
        "total_calls": sum(_metrics["agent_calls"].values()),
        "total_escalations": sum(_metrics["escalations"].values()),
    }

def get_escalation_stats() -> Dict:
    """Get escalation statistics"""
    return {
        "pending": _metrics["escalations"]["pending"] if "pending" in _metrics["escalations"] else 0,
        "resolved": _metrics["escalations"]["resolved"] if "resolved" in _metrics["escalations"] else 0,
        "total": sum(_metrics["escalations"].values()),
    }

class AgentTimer:
    """Context manager for timing agent calls"""
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            latency_ms = (time.time() - self.start_time) * 1000
            record_agent_call(self.agent_type, latency_ms)
            if exc_type:
                record_error(self.agent_type, exc_type.__name__ if exc_type else "unknown")
