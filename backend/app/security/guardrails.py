from typing import Dict, List
import re

# Blocked keywords and patterns
BLOCKED_KEYWORDS = [
    "hack", "exploit", "bypass", "unauthorized access",
    "illegal", "harmful", "dangerous"
]

BLOCKED_PATTERNS = [
    r"password\s*=\s*\w+",
    r"api[_-]?key\s*=\s*\w+",
    r"secret\s*=\s*\w+",
]

def check_guardrails(message: str) -> Dict[str, any]:
    """Check if message passes security guardrails"""
    message_lower = message.lower()
    
    # Check blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        if keyword in message_lower:
            return {
                "allowed": False,
                "reason": f"Contains blocked keyword: {keyword}"
            }
    
    # Check blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return {
                "allowed": False,
                "reason": "Contains sensitive information pattern"
            }
    
    # Check message length (prevent abuse)
    if len(message) > 2000:
        return {
            "allowed": False,
            "reason": "Message too long"
        }
    
    return {
        "allowed": True,
        "reason": "Passed all guardrails"
    }
