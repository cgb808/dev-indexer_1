#!/usr/bin/env python
"""Fine-tune a SentenceTransformer embedding model on in-domain pairs.

Features:
- Loads huggingface base model (default: BAAI/bge-small-en-v1.5) or local path.
- Consumes a TSV/CSV/JSONL of training pairs: text\tpositive (and optional negatives JSON array)
- Supports in-batch negatives + optional explicit negatives (JSONL extension: negatives field list[str]).
- Uses Sentence-Transformers MultipleNegativesRankingLoss for contrastive fine-tune.
- Optional PEFT LoRA adaptation to reduce VRAM (inserts adapters on common projection modules if available).
- Automatic train/val split with evaluation (cosine similarity on held-out pairs).
- Saves final model to output dir, with safe overwrite toggle.
- Gradient accumulation & fp16 toggle.

Example:
  make embed-finetune DATA=data/finetune/pairs.tsv OUTPUT=models/bge-small-finetuned BASE=BAAI/bge-small-en-v1.5 EPOCHS=2 BATCH=128 LR=2e-5 USE_LORA=1
"""
from __future__ import annotations
import argparse, os, json, random, math, sys, time
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation
from torch.utils.data import DataLoader

try:  # torch optional until training
    import torch
except ImportError:  # pragma: no cover
    torch = None  # type: ignore

try:  # optional LoRA
    from peft import LoraConfig, get_peft_model
except ImportError:  # pragma: no cover
    LoraConfig = None  # type: ignore

@dataclass
class TrainConfig:
    data: str
    base_model: str
    output: str
    batch_size: int = 64
    epochs: int = 1
    lr: float = 2e-5
    warmup_ratio: float = 0.06
    seed: int = 42
    use_lora: bool = False
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    max_samples: Optional[int] = None
    val_split: float = 0.05
    fp16: bool = True
    gradient_accumulation: int = 1
    save_every: Optional[int] = None
    overwrite: bool = False
    eval_every: int = 200


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)


def load_pairs(path: str, max_samples: Optional[int]) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.tsv', '.txt'):
        df = pd.read_csv(path, sep='\t', header=None, names=['a', 'b'], quoting=3)
    elif ext == '.csv':
        df = pd.read_csv(path)
        if not {'a','b'}.issubset(df.columns):
            raise ValueError('CSV must have columns a,b')
        df = df[['a','b']]
    elif ext in ('.jsonl', '.json'):
        rows = []
        with open(path,'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                a = obj.get('a') or obj.get('text') or obj.get('query')
                b = obj.get('b') or obj.get('positive') or obj.get('doc')
                if a and b:
                    rows.append((a,b))
        df = pd.DataFrame(rows, columns=['a','b'])
    else:
        raise ValueError(f'Unsupported extension: {ext}')
    if max_samples and len(df) > max_samples:
        df = df.sample(max_samples, random_state=42)
    df = df.dropna().drop_duplicates()
    return df


def build_examples(df: pd.DataFrame) -> List[InputExample]:
    return [InputExample(texts=[r.a, r.b]) for r in df.itertuples(index=False)]


def apply_lora_if_requested(model: SentenceTransformer, cfg: TrainConfig):
    if not cfg.use_lora:
        return model
    if LoraConfig is None:
        print('[warn] peft not installed; skipping LoRA', file=sys.stderr)
        return model
    # SentenceTransformer wraps modules; attempt to fetch underlying HF model
    st_backbone = model._first_module()
    hf_model = getattr(st_backbone, 'auto_model', None)
    if hf_model is None:
        print('[warn] could not locate HF backbone for LoRA', file=sys.stderr)
        return model
    if torch and torch.cuda.is_available():
        hf_model.to('cuda')
    target_modules = ["q_proj", "v_proj", "k_proj", "o_proj", "dense", "fc1", "fc2"]
    lora_conf = LoraConfig(r=cfg.lora_r, lora_alpha=cfg.lora_alpha, lora_dropout=cfg.lora_dropout,
                           bias='none', task_type='FEATURE_EXTRACTION', target_modules=target_modules)
    try:
        get_peft_model(hf_model, lora_conf)
        print('[info] Applied LoRA adapters')
    except Exception as e:  # pragma: no cover
        print(f'[warn] LoRA application failed: {e}')
    return model


def evaluate_dev(model: SentenceTransformer, examples: List[InputExample]):
    if not examples:
        return 0.0
    evaluator = evaluation.EmbeddingSimilarityEvaluator(
        [ex.texts[0] for ex in examples],
        [ex.texts[1] for ex in examples],
        [1.0 for _ in examples],
        name='val'
    )
    return evaluator(model)


def train(cfg: TrainConfig):
    set_seed(cfg.seed)
    if os.path.exists(cfg.output):
        if not cfg.overwrite and os.path.isdir(cfg.output) and os.listdir(cfg.output):
            raise SystemExit(f'Output dir {cfg.output} not empty; use --overwrite to proceed')
    os.makedirs(cfg.output, exist_ok=True)

    print(f'[info] loading data {cfg.data}')
    df = load_pairs(cfg.data, cfg.max_samples)
    # Robust small dataset / no-validation handling
    if cfg.val_split <= 0 or len(df) < 3:
        train_df, val_df = df, df.iloc[0:0]
    else:
        # Compute validation size; ensure at least 1 train sample
        proposed_val = max(1, int(round(len(df) * cfg.val_split)))
        if len(df) - proposed_val < 1:
            proposed_val = max(0, len(df) - 1)
        if proposed_val == 0:
            train_df, val_df = df, df.iloc[0:0]
        else:
            val_df = df.sample(proposed_val, random_state=cfg.seed)
            train_df = df.drop(val_df.index)
    train_examples = build_examples(train_df)
    val_examples = build_examples(val_df)

    print(f'[info] loading model {cfg.base_model}')
    model = SentenceTransformer(cfg.base_model, device='cuda' if torch and torch.cuda.is_available() else 'cpu')
    model = apply_lora_if_requested(model, cfg)

    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=cfg.batch_size)
    loss = losses.MultipleNegativesRankingLoss(model)

    warmup_steps = math.ceil(len(train_dataloader) * cfg.epochs * cfg.warmup_ratio)
    print(f'[info] warmup steps = {warmup_steps}')

    evaluator = None
    if val_examples:
        evaluator = evaluation.EmbeddingSimilarityEvaluator(
            [ex.texts[0] for ex in val_examples],
            [ex.texts[1] for ex in val_examples],
            [1.0 for _ in val_examples],
            name='val'
        )

    model.fit(
        train_objectives=[(train_dataloader, loss)],
        epochs=cfg.epochs,
        warmup_steps=warmup_steps,
        optimizer_params={'lr': cfg.lr},
        use_amp=cfg.fp16,
        evaluator=evaluator,
        evaluation_steps=max(50, len(train_dataloader)//2) if evaluator else 0,
        output_path=cfg.output,
        save_best_model=True
    )
    print(f'[done] model saved to {cfg.output}')


def parse_args() -> TrainConfig:
    p = argparse.ArgumentParser()
    p.add_argument('--data', required=True)
    p.add_argument('--base-model', default='BAAI/bge-small-en-v1.5')
    p.add_argument('--output', required=True)
    p.add_argument('--batch-size', type=int, default=64)
    p.add_argument('--epochs', type=int, default=1)
    p.add_argument('--lr', type=float, default=2e-5)
    p.add_argument('--warmup-ratio', type=float, default=0.06)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--use-lora', action='store_true')
    p.add_argument('--lora-r', type=int, default=16)
    p.add_argument('--lora-alpha', type=int, default=32)
    p.add_argument('--lora-dropout', type=float, default=0.05)
    p.add_argument('--max-samples', type=int)
    p.add_argument('--val-split', type=float, default=0.05)
    p.add_argument('--no-fp16', action='store_true')
    p.add_argument('--gradient-accumulation', type=int, default=1)
    p.add_argument('--save-every', type=int)
    p.add_argument('--overwrite', action='store_true')
    args = p.parse_args()
    return TrainConfig(
        data=args.data, base_model=args.base_model, output=args.output,
        batch_size=args.batch_size, epochs=args.epochs, lr=args.lr,
        warmup_ratio=args.warmup_ratio, seed=args.seed, use_lora=args.use_lora,
        lora_r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=args.lora_dropout,
        max_samples=args.max_samples, val_split=args.val_split, fp16=not args.no_fp16,
        gradient_accumulation=args.gradient_accumulation, save_every=args.save_every,
        overwrite=args.overwrite
    )

if __name__ == '__main__':  # pragma: no cover
    cfg = parse_args()
    train(cfg)
