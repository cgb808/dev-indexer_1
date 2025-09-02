#!/usr/bin/env python
"""Quantize a saved SentenceTransformer / HF model to 4-bit or 8-bit using bitsandbytes.

Example:
  python dev-indexer_1/scripts/quantize_embedding_model.py \
      --model-path models/bge-small-finetuned \
      --output models/bge-small-finetuned-int8 --dtype int8
"""
import argparse, os, shutil, sys

try:
    import torch
    import bitsandbytes as bnb  # noqa: F401
except ImportError:
    torch = None

from sentence_transformers import SentenceTransformer


def quantize(model_path: str, output: str, dtype: str):
    if torch is None:
        raise SystemExit('torch/bitsandbytes not installed; install requirements-train.txt')
    if os.path.exists(output):
        raise SystemExit(f'Output {output} exists')
    os.makedirs(output, exist_ok=True)

    model = SentenceTransformer(model_path, device='cpu')
    # We will reload underlying auto_model and apply quantization config by saving adapter notionally.
    backbone = model._first_module()
    hf_model = getattr(backbone, 'auto_model', None)
    if hf_model is None:
        raise SystemExit('Could not locate underlying HF model for quantization')
    if dtype not in ('int8','int4'):
        raise SystemExit('--dtype must be int8 or int4')

    load_kwargs = {}
    if dtype == 'int8':
        load_kwargs = dict(load_in_8bit=True, device_map='auto')
    else:
        load_kwargs = dict(load_in_4bit=True, device_map='auto')

    # Re-load the model with quantization (simple approach)
    from transformers import AutoModel
    from transformers import AutoConfig
    name_or_path = hf_model.name_or_path
    config = AutoConfig.from_pretrained(name_or_path)
    q_model = AutoModel.from_pretrained(name_or_path, **load_kwargs, config=config)

    # Save quantized (weights inside q_model) and reuse tokenizer / sentence-transformers config.
    q_model.save_pretrained(output)
    tokenizer = getattr(backbone, 'tokenizer', None)
    if tokenizer:
        tokenizer.save_pretrained(output)
    # Copy sentence-transformers specific files
    for fname in ('config.json','modules.json'):  # typical st files
        src = os.path.join(model_path, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(output, fname))
    print(f'[done] quantized model saved to {output}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-path', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--dtype', default='int8', choices=['int8','int4'])
    args = ap.parse_args()
    quantize(args.model_path, args.output, args.dtype)

if __name__ == '__main__':
    main()
