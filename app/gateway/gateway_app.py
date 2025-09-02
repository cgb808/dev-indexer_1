import hashlib
import json
import logging
import os
import time
from typing import Iterator, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader

# Configuration (env overrides)
API_KEY = os.getenv("API_GATEWAY_KEY", "changeme")
DATASET_BASE = os.getenv("CURATED_DATASET_DIR", "/DEV_ZFS/datasets/curated")
CURATED_FILE = os.getenv("CURATED_FILE", "combined_curated.jsonl")
PACKED_FILE = os.getenv("PACKED_FILE", "packed_gemma2048.jsonl")
MANIFEST_FILE = os.getenv("MANIFEST_FILE", "manifest_curated.json")
DATASET_SHARE_KEY = os.getenv("DATASET_SHARE_KEY", "change-dataset-key")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Structured logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("gateway")

app = FastAPI(title="ZenGlow Gateway", version="1.0.0")


async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if api_key != API_KEY:
        logger.warning("Unauthorized access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )


@app.middleware("http")
async def audit_log(request: Request, call_next):
    logger.info("Request: %s %s", request.method, request.url)
    response = await call_next(request)
    logger.info("Response status: %s", response.status_code)
    return response


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
async def ready():
    # Placeholder: add downstream readiness checks
    return {"ready": True}


@app.get("/admin/ping", dependencies=[Depends(verify_api_key)], tags=["admin"])
async def admin_ping():
    return {"ping": "pong"}


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
):  # pragma: no cover - defensive
    logger.error("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ---------------- Dataset Distribution -----------------


def _iter_file_lines(path: str) -> Iterator[bytes]:
    with open(path, "rb") as f:
        for line in f:
            yield line


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _dataset_path(packed: bool) -> str:
    fname = PACKED_FILE if packed else CURATED_FILE
    return os.path.join(DATASET_BASE, fname)


def _manifest_path() -> str:
    return os.path.join(DATASET_BASE, MANIFEST_FILE)


def _verify_dataset_key(key: Optional[str]):
    if key != DATASET_SHARE_KEY:
        raise HTTPException(status_code=401, detail="Invalid dataset key")


@app.get("/dataset/manifest", tags=["dataset"])
async def dataset_manifest(key: str, packed: bool = False):
    _verify_dataset_key(key)
    manifest_path = _manifest_path()
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        raise HTTPException(404, detail="Manifest not found")
    ds_path = _dataset_path(packed)
    if not os.path.exists(ds_path):
        raise HTTPException(404, detail="Dataset file not found")
    size = os.path.getsize(ds_path)
    checksum = _file_sha256(ds_path)
    signed = {
        "dataset": os.path.basename(ds_path),
        "size_bytes": size,
        "sha256": checksum,
        "packed": packed,
        "generated_at": int(time.time()),
        "manifest": manifest,
    }
    return signed


@app.get("/dataset/stream", tags=["dataset"])
async def dataset_stream(key: str, packed: bool = False):
    _verify_dataset_key(key)
    path = _dataset_path(packed)
    if not os.path.exists(path):
        raise HTTPException(404, detail="Dataset file not found")
    headers = {"X-Dataset-Name": os.path.basename(path)}
    return StreamingResponse(
        _iter_file_lines(path), media_type="application/x-ndjson", headers=headers
    )
