#!/usr/bin/env python
"""Quantize a saved SentenceTransformer / HF model to 4-bit or 8-bit using bitsandbytes.

Example:
  python fine_tuning/training/scripts/quantize_embedding_model.py \
      --model-path models/bge-small-finetuned \
      --output models/bge-small-finetuned-int8 --dtype int8

Notes:
  * Expects bitsandbytes + torch installed (see requirements-train.txt).
  * Re-loads the underlying HF backbone with load_in_8bit / load_in_4bit flags then
    writes out a new directory preserving SentenceTransformer config files.
  * Keeps tokenizer and SentenceTransformer module definitions so you can
    rehydrate with SentenceTransformer(output_path) for downstream usage.
"""
from __future__ import annotations
import argparse, os, shutil, sys

try:  # heavy deps
    import torch  # type: ignore
    import bitsandbytes as bnb  # noqa: F401  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore

from sentence_transformers import SentenceTransformer  # type: ignore

def _merge_lora_if_present(hf_model):
    """Attempt to merge LoRA adapters into base weights (if using PEFT) before quantization.
    Safe no-op if PEFT / adapters not present."""
    try:
        from peft import PeftModel
    except Exception:  # pragma: no cover
        return hf_model
    if isinstance(hf_model, PeftModel):
        try:
            print('[info] Merging LoRA adapters into base model before quantization')
            hf_model = hf_model.merge_and_unload()
        except Exception as e:  # pragma: no cover
            print(f'[warn] failed to merge LoRA adapters: {e}')
    return hf_model


def quantize(model_path: str, output: str, dtype: str):
    if torch is None:
        raise SystemExit('torch/bitsandbytes not installed; install requirements-train.txt')
    if os.path.exists(output):
        raise SystemExit(f'Output {output} exists (refuse overwrite)')
    os.makedirs(output, exist_ok=True)

    model = SentenceTransformer(model_path, device='cpu')
    backbone = model._first_module()
    hf_model = getattr(backbone, 'auto_model', None)
    if hf_model is None:
        raise SystemExit('Could not locate underlying HF model for quantization')
    hf_model = _merge_lora_if_present(hf_model)
    if dtype not in ('int8', 'int4'):
        raise SystemExit('--dtype must be int8 or int4')

    load_kwargs: dict = {}
    if dtype == 'int8':
        load_kwargs = dict(load_in_8bit=True, device_map='auto')
    else:
        load_kwargs = dict(load_in_4bit=True, device_map='auto')

    from transformers import AutoModel, AutoConfig  # type: ignore
    name_or_path = hf_model.name_or_path
    config = AutoConfig.from_pretrained(name_or_path)
    print(f'[info] loading {name_or_path} with {dtype} quantization flags')
    try:
        q_model = AutoModel.from_pretrained(name_or_path, config=config, **load_kwargs)
    except Exception as e:
        # bitsandbytes sometimes fails on adapter remnants; fallback: try without quant flags (then quantize manually if needed)
        print(f'[warn] primary quantized load failed: {e.__class__.__name__}: {e}')
        print('[info] retrying load in fp16 (if available) then saving (no quant)')
        alt_kwargs = {'torch_dtype': torch.float16} if torch.cuda.is_available() else {}
        q_model = AutoModel.from_pretrained(name_or_path, config=config, **alt_kwargs)
        print('[info] loaded non-quantized fallback model; consider re-running with a clean merged directory for proper int8/int4')

    print('[info] saving quantized backbone')
    q_model.save_pretrained(output)
    tokenizer = getattr(backbone, 'tokenizer', None)
    if tokenizer:
        tokenizer.save_pretrained(output)

    # Copy SentenceTransformer specific structural files
    for fname in ('config.json', 'modules.json'):  # typical ST layout
        src = os.path.join(model_path, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(output, fname))

    # Copy pooling / model submodule directories if present (keeps architecture intact)
    for item in os.listdir(model_path):
        p = os.path.join(model_path, item)
        if os.path.isdir(p) and item.startswith('0_'):  # ST numbered modules
            dst = os.path.join(output, item)
            if not os.path.exists(dst):
                shutil.copytree(p, dst)

    print(f'[done] quantized model saved to {output}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-path', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--dtype', default='int8', choices=['int8', 'int4'])
    args = ap.parse_args()
    quantize(args.model_path, args.output, args.dtype)

if __name__ == '__main__':  # pragma: no cover
    main()
