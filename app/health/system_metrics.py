"""System metrics collection (CPU, memory, GPU) with lightweight caching.

This module is isolated so we can silence mypy noise from dynamic libs.
"""

# mypy: ignore-errors
from __future__ import annotations

import os
import subprocess
import time
from typing import Any, Dict, List

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

try:
    import pynvml  # type: ignore
except Exception:  # pragma: no cover
    pynvml = None  # type: ignore

_CACHE: Dict[str, Any] | None = None
_CACHE_TS: float | None = None
_TTL = 2.0


def _gpus_via_pynvml() -> List[Dict[str, Any]]:
    g: List[Dict[str, Any]] = []
    if not pynvml:
        return g
    try:
        pynvml.nvmlInit()  # type: ignore
        count = int(pynvml.nvmlDeviceGetCount())  # type: ignore
        for i in range(count):
            h = pynvml.nvmlDeviceGetHandleByIndex(i)  # type: ignore
            mem = pynvml.nvmlDeviceGetMemoryInfo(h)  # type: ignore
            util = pynvml.nvmlDeviceGetUtilizationRates(h)  # type: ignore
            temp = int(pynvml.nvmlDeviceGetTemperature(h, pynvml.NVML_TEMPERATURE_GPU))  # type: ignore
            raw_name = pynvml.nvmlDeviceGetName(h)  # type: ignore
            name = raw_name.decode() if isinstance(raw_name, bytes) else str(raw_name)
            total_mb = int(mem.total / (1024 * 1024))
            used_mb = int(mem.used / (1024 * 1024))
            g.append(
                {
                    "index": i,
                    "name": name,
                    "memory_total_mb": total_mb,
                    "memory_used_mb": used_mb,
                    "memory_percent": (
                        round(used_mb / total_mb * 100, 2) if total_mb else 0.0
                    ),
                    "utilization_percent": getattr(util, "gpu", None),
                    "temperature_c": temp,
                }
            )
    except Exception:
        return []
    return g


def _gpus_via_nvidia_smi() -> List[Dict[str, Any]]:
    try:
        out = (
            subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu",
                    "--format=csv,noheader,nounits",
                ],
                stderr=subprocess.DEVNULL,
                timeout=1.5,
            )
            .decode()
            .strip()
        )
        g: List[Dict[str, Any]] = []
        if out:
            for idx, line in enumerate(out.splitlines()):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) == 5:
                    name, mem_total, mem_used, util_gpu, temp = parts
                    total_mb = int(mem_total)
                    used_mb = int(mem_used)
                    g.append(
                        {
                            "index": idx,
                            "name": name,
                            "memory_total_mb": total_mb,
                            "memory_used_mb": used_mb,
                            "memory_percent": (
                                round(used_mb / total_mb * 100, 2) if total_mb else 0.0
                            ),
                            "utilization_percent": float(util_gpu),
                            "temperature_c": int(temp),
                        }
                    )
        return g
    except Exception:
        return []


def _gather_gpu() -> List[Dict[str, Any]]:
    g = _gpus_via_pynvml()
    if g:
        return g
    return _gpus_via_nvidia_smi()


def get_system_metrics() -> Dict[str, Any]:  # runtime path
    global _CACHE, _CACHE_TS
    now = time.time()
    if _CACHE and _CACHE_TS and (now - _CACHE_TS) < _TTL:
        return _CACHE
    data: Dict[str, Any] = {}
    if psutil:
        try:
            data["cpu_percent"] = float(psutil.cpu_percent(interval=None))
            data["cpu_count"] = int(psutil.cpu_count(logical=True) or 0)
            try:
                la = os.getloadavg()
                data["load_avg"] = tuple(float(x) for x in la)
            except Exception:
                pass
            vm = psutil.virtual_memory()
            data["memory"] = {
                "total_bytes": int(vm.total),
                "available_bytes": int(vm.available),
                "used_bytes": int(vm.used),
                "percent": float(vm.percent),
            }
            sm = psutil.swap_memory()
            data["swap"] = {
                "total_bytes": int(sm.total),
                "used_bytes": int(sm.used),
                "percent": float(sm.percent),
            }
        except Exception:
            pass
    data["gpu"] = _gather_gpu()
    _CACHE = data
    _CACHE_TS = now
    return data
