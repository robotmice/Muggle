"""Structured JSON-line logging for generation monitoring and issue diagnosis.

Log Field Dictionary
--------------------
ts               ISO-8601 timestamp
level            Log level (INFO, WARNING, ERROR)
logger           Python logger name
event            Human-readable event description
request_id       UUID per HTTP request, correlates all log lines for one turn
thread_id        Conversation thread ID from frontend
node             Pipeline node name (intent_check, query_rewrite, retrieval, inquiry, validation, fallback)
duration_ms      Wall-clock duration of the node in milliseconds
is_refusal       Whether the final response was a refusal (true/false)
refusal_reason   Why the response was refused (intent_fail / validation_fail / fallback)
n_results        Number of retrieved documents after filtering
token_estimate   Rough estimate of LLM tokens consumed (input + output)
cache_hit        Whether the query was served from cache (true/false)
error_type       Exception class name when an error occurs
response_len     Length of the final response string
attempt_count    Number of validation retry attempts
"""

import json
import logging
import sys
import time
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
thread_id_var: ContextVar[str] = ContextVar("thread_id", default="")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data: dict = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        rid = request_id_var.get()
        if rid:
            data["request_id"] = rid
        tid = thread_id_var.get()
        if tid:
            data["thread_id"] = tid

        for key in (
            "node", "duration_ms", "is_refusal", "refusal_reason",
            "n_results", "token_estimate", "cache_hit",
            "error_type", "response_len", "attempt_count",
        ):
            val = getattr(record, key, None)
            if val is not None:
                data[key] = val

        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: int = logging.INFO):
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    # Remove any existing handlers to avoid duplicate output
    root.handlers.clear()
    root.addHandler(handler)


def log_duration(logger: logging.Logger, node: str, t0: float, **kwargs):
    """Log a node completion with consistent duration calculation (ms)."""
    duration_ms = round((time.monotonic() - t0) * 1000, 1)
    logger.info(f"{node} completed", extra={"node": node, "duration_ms": duration_ms, **kwargs})
