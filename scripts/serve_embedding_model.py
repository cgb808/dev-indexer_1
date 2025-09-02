#!/usr/bin/env python
"""Serve a (fine-tuned or base) embedding model via FastAPI compatible with existing EMBED_ENDPOINT.

Endpoint:
  POST /embed {"inputs": ["text1", "text2", ...]}
Response:
  {"embeddings": [[...],[...],...], "model": name, "dim": n}

Supports:
- Loading quantized (int8/int4) model if previously saved.
- Optional batch size and device selection.
- Simple concurrency limiting.

Example:
  python dev-indexer_1/scripts/serve_embedding_model.py --model models/bge-small-finetuned --port 8000
"""
from __future__ import annotations
import argparse, os, time, asyncio
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise SystemExit('Install training requirements (requirements-train.txt) to serve model.')

app = FastAPI()
model: SentenceTransformer | None = None
sem: asyncio.Semaphore | None = None
model_name: str = ''

class EmbedRequest(BaseModel):
    inputs: List[str]

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    dim: int

@app.post('/embed', response_model=EmbedResponse)
async def embed(req: EmbedRequest):
    if model is None:
        raise HTTPException(503, 'model not loaded')
    if not req.inputs:
        return EmbedResponse(embeddings=[], model=model_name, dim=0)
    if sem:
        async with sem:
            return await _embed(req.inputs)
    else:
        return await _embed(req.inputs)

async def _embed(texts: List[str]) -> EmbedResponse:
    loop = asyncio.get_event_loop()
    embs = await loop.run_in_executor(None, model.encode, texts)
    embs = embs.tolist()
    dim = len(embs[0]) if embs else 0
    return EmbedResponse(embeddings=embs, model=model_name, dim=dim)

@app.get('/healthz')
async def health():
    return {'status': 'ok', 'model': model_name}

@app.get('/info')
async def info():
    return {'model': model_name, 'device': str(next(model._first_module().parameters()).device) if model else None}


def load_model(path: str, device: str):
    global model, model_name
    start = time.time()
    model = SentenceTransformer(path, device=device)
    model_name = path
    dur = time.time() - start
    print(f'[info] model loaded in {dur:.2f}s on {device}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--device', default='cuda' if os.environ.get('USE_CUDA','1') == '1' else 'cpu')
    parser.add_argument('--concurrency', type=int, default=4)
    args = parser.parse_args()

    if args.device.startswith('cuda'):
        import torch
        if not torch.cuda.is_available():
            print('[warn] cuda requested but not available; falling back to cpu')
            args.device = 'cpu'

    load_model(args.model, args.device)
    global sem
    sem = asyncio.Semaphore(args.concurrency) if args.concurrency > 0 else None
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
