"""
Metrics and Performance Tracking System
Tracks agent performance, latency, escalation rates, and more
"""

from typing import Dict
from collections import defaultdict
import time

# -------------------------------------------------
# In-memory metrics store
# (Production: Redis / Prometheus / Time-series DB)
# -------------------------------------------------

_metrics = {
    "agent_calls": defaultdict(int),
    "agent_latency": defaultdict(list),
    "escalations": defaultdict(int),
    "intent_distribution": defaultdict(int),
    "errors": defaultdict(int),
}


# -------------------------------------------------
# Recorders
# -------------------------------------------------

def record_agent_call(agent_type: str, latency_ms: float):
    """Record an agent call and its latency"""
    _metrics["agent_calls"][agent_type] += 1
    _metrics["agent_latency"][agent_type].append(latency_ms)

    # Keep only last 1000 samples
    if len(_metrics["agent_latency"][agent_type]) > 1000:
        _metrics["agent_latency"][agent_type] = \
            _metrics["agent_latency"][agent_type][-1000:]


def record_intent(intent: str):
    """Record intent classification"""
    _metrics["intent_distribution"][intent] += 1


def record_escalation(agent_type: str):
    """Record an escalation"""
    _metrics["escalations"][agent_type] += 1


def record_error(agent_type: str, error_type: str):
    """Record agent error"""
    _metrics["errors"][f"{agent_type}_{error_type}"] += 1


# -------------------------------------------------
# Aggregation
# -------------------------------------------------

def get_metrics() -> Dict:
    """Return all collected metrics"""
    agent_stats = {}

    for agent_type, total_calls in _metrics["agent_calls"].items():
        latencies = _metrics["agent_latency"][agent_type]

        agent_stats[agent_type] = {
            "total_calls": total_calls,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "escalations": _metrics["escalations"][agent_type],
            "escalation_rate": (
                _metrics["escalations"][agent_type] / total_calls
                if total_calls > 0
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
    """Return escalation summary"""
    return {
        "total": sum(_metrics["escalations"].values()),
        "by_agent": dict(_metrics["escalations"]),
    }


# -------------------------------------------------
# Timing Context Manager
# -------------------------------------------------

class AgentTimer:
    """
    Context manager to track agent execution latency.

    Usage:
        with AgentTimer("support_agent"):
            generate_response(...)
    """

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = (time.time() - self.start_time) * 1000
        record_agent_call(self.agent_type, latency_ms)

        if exc_type:
            record_error(
                self.agent_type,
                exc_type.__name__ if exc_type else "unknown"
            )
