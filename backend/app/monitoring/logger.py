import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = "app.log"

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# ---------------- Logger Setup ----------------

def setup_logger():
    logger = logging.getLogger("ai_customer_support")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            LOG_PATH,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Global logger instance
_logger = setup_logger()


# ---------------- Logging Helper ----------------

def log_event(event: str, data: dict | None = None):
    """
    Log structured application events.

    Example:
        log_event("CHAT_REQUEST", {"intent": "refund", "escalated": True})
    """
    if data is None:
        data = {}

    _logger.info(f"{event} | {data}")
