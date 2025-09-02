"""Lightweight in-process metrics (no external deps).

Designed for local observability / debugging without Prometheus overhead.
Keeps rolling latency samples (naive list capped) and simple counters.
Thread-safety: minimal; FastAPI default Uvicorn workers (single process) so
basic locking via threading.Lock.
"""

from __future__ import annotations

import threading
import time
from typing import Dict, List

_lock = threading.Lock()
_counters: Dict[str, int] = {
    "requests_total": 0,
    "llm_calls_total": 0,
    "retrieval_calls_total": 0,
    "errors_total": 0,
}
_latency_samples: Dict[str, List[float]] = {
    "llm_ms": [],
    "retrieval_ms": [],
    "total_ms": [],
    # Newly added stage timings (populated by /rag/query integration):
    "embed_ms": [],
    "feature_ms": [],
    "ltr_ms": [],
    "fusion_ms": [],
    "pipeline_ms": [],  # server-side pipeline total from ranking_router
}
_MAX_SAMPLES = 500


def inc(name: str, delta: int = 1) -> None:
    with _lock:
        _counters[name] = _counters.get(name, 0) + delta


def observe(latency_name: str, value_ms: float) -> None:
    with _lock:
        arr = _latency_samples.setdefault(latency_name, [])
        arr.append(value_ms)
        if len(arr) > _MAX_SAMPLES:
            # Drop oldest half to avoid O(n) shift
            del arr[: len(arr) // 2]


def snapshot() -> Dict[str, object]:
    with _lock:
        latency: Dict[str, Dict[str, float]] = {}
        for k, arr in _latency_samples.items():
            if not arr:
                latency[k] = {}
                continue
            sorted_arr = sorted(arr)
            n = len(sorted_arr)

            def pct(p: float) -> float:
                if n == 0:
                    return 0.0
                idx = min(n - 1, int(p * n) - 1)
                return sorted_arr[idx]

            latency[k] = {
                "count": float(n),
                "avg": sum(sorted_arr) / n,
                "p50": pct(0.50),
                "p90": pct(0.90),
                "p95": pct(0.95),
                "p99": pct(0.99),
                "max": sorted_arr[-1],
            }
        return {"counters": dict(_counters), "latency": latency}


class Timer:
    def __init__(self):
        self.start = time.time()

    def ms(self) -> float:
        return (time.time() - self.start) * 1000
