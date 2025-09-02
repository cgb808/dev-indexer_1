"""Central logging configuration.

Goals:
  * Single place to configure root logger & format.
  * Support plain text (default) or JSON logs via LOG_JSON=true.
  * Honor LOG_LEVEL env (default INFO).
  * Attach contextual extra fields easily (helper function).

The in‑memory UI log buffer in ``log_buffer`` hooks into the root logger, so
ensuring we standardize formatting early gives immediate benefit to the
debug panel and any future shipping (stdout scraping, etc.).
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Any, Dict

_INITIALIZED = False


class _RequestContextFilter(logging.Filter):
    """Inject per-request correlation identifiers if present in context vars.

    Simplest scaffold: if LOG_REQUEST_IDS=1 and record lacks request_id, attach a pseudo UUID4.
    In future integrate with middleware that sets contextvar for trace / span ids.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        if os.getenv("LOG_REQUEST_IDS", "0") in {
            "1",
            "true",
            "on",
            "yes",
        } and not hasattr(record, "request_id"):
            # Cheap generation (could be replaced by contextvar lookup)
            setattr(record, "request_id", uuid.uuid4().hex[:12])
        return True


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        base: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created))
            + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        # Selected extras
        for key in ("component", "event", "qid", "request_id"):
            if hasattr(record, key):
                base[key] = getattr(record, key)
        return json.dumps(base, ensure_ascii=False)


def _build_plain_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def init_logging(force: bool = False) -> None:
    global _INITIALIZED
    if _INITIALIZED and not force:
        return
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    json_mode = os.getenv("LOG_JSON", "false").lower() == "true"
    root = logging.getLogger()
    root.setLevel(level)
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter() if json_mode else _build_plain_formatter())
    handler.addFilter(_RequestContextFilter())
    root.addHandler(handler)
    _INITIALIZED = True
    logging.getLogger(__name__).debug(
        "logging initialized",
        extra={"component": "logging", "event": "init", "json": json_mode},
    )


def with_ctx(logger: logging.Logger, **extra: Any):  # pragma: no cover - thin helper
    """Return a function for structured logging with fixed extras.

    Example:
            log_info = with_ctx(logging.getLogger(__name__), component="startup")
            log_info("Service starting")
    """

    def _log(message: str, level: int = logging.INFO, **kw: Any):
        data = {**extra, **kw}
        logger.log(level, message, extra=data)  # type: ignore[arg-type]

    return _log


__all__ = ["init_logging", "with_ctx"]
