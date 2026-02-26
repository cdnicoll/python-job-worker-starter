"""Structured logging with request_id support."""
import json
import logging
import sys
from datetime import datetime
from typing import Any, Optional


class StructuredFormatter(logging.Formatter):
    """JSON-structured formatter; includes request_id when in logRecord."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id") and record.request_id:
            log_obj["request_id"] = record.request_id
        return json.dumps(log_obj)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with structured (JSON) format; include request_id when available."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        try:
            from src.models.config import load_settings
            level = getattr(logging, load_settings().log_level.upper(), logging.INFO)
        except Exception:
            level = logging.INFO
        logger.setLevel(level)
    return logger


def setup_logging(settings: Any) -> None:
    """Configure logging with structured (JSON) format."""
    level = getattr(logging, getattr(settings, "log_level", "INFO").upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logging.root.addHandler(handler)
    logging.root.setLevel(level)
