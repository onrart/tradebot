from __future__ import annotations

import json
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any

_RECENT_LOGS: deque[str] = deque(maxlen=300)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra_data = getattr(record, "extra_data", None)
        if isinstance(extra_data, dict):
            payload.update(extra_data)
        line = json.dumps(payload, ensure_ascii=False)
        _RECENT_LOGS.appendleft(line)
        return line


def get_logger(name: str = "tradebot") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def get_recent_logs(limit: int = 100) -> list[str]:
    return list(_RECENT_LOGS)[:limit]


def sanitize_secret(value: str | None) -> str:
    if not value:
        return ""
    return f"{value[:3]}***{value[-2:]}" if len(value) > 6 else "***"
