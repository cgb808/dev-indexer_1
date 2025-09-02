#!/usr/bin/env python3
"""Shared JSON logging utility for workers.

Usage:
  from worker_logging import get_logger
  log = get_logger('async_embed')
  log.info('batch_complete', rows=32, took_ms=1234)

Logs are emitted as single-line JSON to stdout.
"""
from __future__ import annotations
import os, sys, json, time, socket, threading
from typing import Any

_LOG_LOCK = threading.Lock()
_HOST = socket.gethostname()
_ENV = os.getenv('APP_ENV','dev')
_SERVICE = os.getenv('SERVICE_NAME','worker')

class JsonLogger:
    def __init__(self, component: str):
        self.component = component
    def _emit(self, level: str, event: str, **fields: Any):
        rec = {
            'ts': time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime()),
            'level': level,
            'event': event,
            'component': self.component,
            'service': _SERVICE,
            'env': _ENV,
            'host': _HOST,
        }
        rec.update(fields)
        line = json.dumps(rec, ensure_ascii=False, separators=(',',':'))
        with _LOG_LOCK:
            print(line, file=sys.stdout, flush=True)
    def info(self, event: str, **fields: Any):
        self._emit('INFO', event, **fields)
    def warn(self, event: str, **fields: Any):  # alias
        self._emit('WARN', event, **fields)
    def error(self, event: str, **fields: Any):
        self._emit('ERROR', event, **fields)

def get_logger(component: str) -> JsonLogger:
    return JsonLogger(component)

if __name__ == '__main__':  # simple self-test
    log = get_logger('selftest')
    log.info('hello', answer=42)
