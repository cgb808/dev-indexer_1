#!/usr/bin/env python3
"""General Phi3 (Jeeves Base) LoRA Fine-Tune Script.

Features:
- Reads JSONL dataset with (instruction,response) or (prompt,output)
- Applies LoRA adapters via PEFT
- Supports bf16 if available
- Streams simple progress logs

Usage:
  python fine_tuning/training/scripts/finetune_phi3_general.py \
    --config fine_tuning/training/configs/phi3_general_lora.yaml \
    --dataset data/general/jeeves_general_dataset.jsonl

Minimal Makefile target available: `make finetune-phi3-general DATASET=...`
"""
from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List

import torch
import yaml
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from torch.utils.data import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          DataCollatorForLanguageModeling, Trainer,
                          TrainingArguments, set_seed)


@dataclass
class Record:
    prompt: str
    response: str


class GeneralJsonlDataset(Dataset):
    def __init__(self, path: str, tokenizer, max_length: int = 2048):
        self.path = path
        self.examples: List[Record] = []
        self.tokenizer = tokenizer
        self.max_length = max_length
        with open(path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                instr = obj.get("instruction") or obj.get("prompt") or ""
                resp = obj.get("response") or obj.get("output") or ""
                if not instr or not resp:
                    continue
                self.examples.append(Record(instr, resp))
        if not self.examples:
            raise ValueError(f"No valid examples loaded from {path}")
        print(f"[dataset] Loaded {len(self.examples)} examples from {path}")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        record = self.examples[idx]
        # Simple instruction-response concatenation
        prompt = f"<|user|> {record.prompt}\n<|assistant|>"
        target = record.response
        full = prompt + " " + target
        tokens = self.tokenizer(
            full,
            truncation=True,
            max_length=self.max_length,
            padding=False,
            return_tensors="pt",
        )
        input_ids = tokens.input_ids[0]
        # Labels are full sequence; could mask prompt tokens if desired
        return {"input_ids": input_ids, "labels": input_ids.clone()}


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def build_lora(config: Dict[str, Any]) -> LoraConfig:
    lc = config.get("lora", {})
    return LoraConfig(
        r=lc.get("r", 16),
        lora_alpha=lc.get("alpha", 32),
        lora_dropout=lc.get("dropout", 0.05),
        bias=lc.get("bias", "none"),
        target_modules=lc.get("target_modules", None),
        task_type=lc.get("task_type", "CAUSAL_LM"),
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument(
        "--dataset", required=False, help="Override dataset path from config"
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--merge-lora",
        action="store_true",
        help="Merge LoRA weights into base and save final model",
    )
    args = p.parse_args()

    set_seed(args.seed)
    cfg = load_config(args.config)
    dataset_path = args.dataset or cfg["dataset_path"]
    out_dir = cfg["output_dir"]
    os.makedirs(out_dir, exist_ok=True)

    model_name = cfg["model_name"]
    print(f"[config] Base model: {model_name}")
    print(f"[config] Dataset: {dataset_path}")

    tokenizer = AutoTokenizer.from_pretrained(
        model_name, trust_remote_code=cfg.get("trust_remote_code", True)
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    torch_dtype = (
        torch.bfloat16
        if cfg.get("bf16", False)
        and torch.cuda.is_available()
        and torch.cuda.is_bf16_supported()
        else torch.float16
    )
    print(f"[device] Using dtype={torch_dtype}")

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        device_map="auto",
        trust_remote_code=cfg.get("trust_remote_code", True),
    )

    # Prepare for k-bit training if already quantized (optional future enhancement)
    model = prepare_model_for_kbit_training(model)

    lora_cfg = build_lora(cfg)
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    dataset = GeneralJsonlDataset(
        dataset_path, tokenizer, max_length=cfg.get("max_seq_length", 2048)
    )

    training_args = TrainingArguments(
        output_dir=out_dir,
        num_train_epochs=cfg.get("num_epochs", 1),
        per_device_train_batch_size=cfg.get("per_device_train_batch_size", 2),
        gradient_accumulation_steps=cfg.get("gradient_accumulation_steps", 8),
        learning_rate=cfg.get("learning_rate", 2e-4),
        weight_decay=cfg.get("weight_decay", 0.0),
        warmup_ratio=cfg.get("warmup_ratio", 0.03),
        logging_steps=cfg.get("logging_steps", 25),
        save_strategy=cfg.get("save_strategy", "epoch"),
        bf16=cfg.get("bf16", False),
        fp16=not cfg.get("bf16", False),
        lr_scheduler_type=cfg.get("lr_scheduler_type", "cosine"),
        max_grad_norm=cfg.get("max_grad_norm", 1.0),
        report_to=[],
    )

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=collator,
    )

    trainer.train()
    trainer.save_model(out_dir + "/lora_adapter")
    tokenizer.save_pretrained(out_dir + "/lora_adapter")
    print(f"[save] LoRA adapter saved to {out_dir}/lora_adapter")

    if args.merge_lora:
        print("[merge] Merging LoRA weights into base model (may increase size)...")
        merged_model = model.merge_and_unload()
        merged_path = out_dir + "/merged_model"
        os.makedirs(merged_path, exist_ok=True)
        merged_model.save_pretrained(merged_path, safe_serialization=True)
        tokenizer.save_pretrained(merged_path)
        print(f"[merge] Merged model saved at {merged_path}")

    # Write minimal metadata
    meta = {
        "base_model": model_name,
        "dataset_path": dataset_path,
        "num_examples": len(dataset),
        "epochs": cfg.get("num_epochs", 1),
        "lora": cfg.get("lora", {}),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(os.path.join(out_dir, "training_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[save] Metadata written to {out_dir}/training_metadata.json")


if __name__ == "__main__":
    main()
