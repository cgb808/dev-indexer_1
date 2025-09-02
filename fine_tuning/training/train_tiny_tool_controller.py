#!/usr/bin/env python3
"""
Fine-tune a tiny quantized model for ultra-fast tool control.
This model will classify user inputs and route to appropriate tools in <100ms.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List

import torch
from datasets import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          DataCollatorForLanguageModeling, Trainer,
                          TrainingArguments)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolControlDataset:
    """Custom dataset for tool control fine-tuning."""

    def __init__(self, jsonl_file: str, tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = self._load_examples(jsonl_file)

    def _load_examples(self, jsonl_file: str) -> List[Dict]:
        """Load and format examples for training."""
        examples = []
        with open(jsonl_file, "r") as f:
            for line in f:
                data = json.loads(line.strip())
                formatted_example = self._format_example(data)
                examples.append(formatted_example)

        logger.info(f"Loaded {len(examples)} training examples")
        return examples

    def _format_example(self, data: Dict) -> Dict:
        """Format example for tool control training."""
        user_input = data["user_input"]
        classification = data["tool_classification"]

        # Create structured prompt for tiny model
        prompt = f"""<|system|>You are a lightning-fast tool classifier. Analyze the user input and output the tool classification in JSON format.<|end|>
<|user|>{user_input}<|end|>
<|assistant|>{json.dumps(classification, indent=None)}<|end|>"""

        # Tokenize
        encoding = self.tokenizer(
            prompt,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": encoding[
                "input_ids"
            ].squeeze(),  # For causal LM, labels = input_ids
        }

    def to_hf_dataset(self) -> Dataset:
        """Convert to HuggingFace Dataset format."""
        formatted_data = {
            "input_ids": [ex["input_ids"] for ex in self.examples],
            "attention_mask": [ex["attention_mask"] for ex in self.examples],
            "labels": [ex["labels"] for ex in self.examples],
        }
        return Dataset.from_dict(formatted_data)


class TinyToolControlTrainer:
    """Trainer for tiny tool control model."""

    def __init__(
        self,
        model_name: str = "microsoft/Phi-3-mini-4k-instruct",
        dataset_path: str = "fine_tuning/datasets/tool_control/tool_control_training.jsonl",
        output_dir: str = "models/tiny_tool_controller",
        max_length: int = 512,
    ):

        self.model_name = model_name
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.max_length = max_length

        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Add pad token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model in 4-bit for memory efficiency
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            load_in_4bit=True,  # For memory efficiency during training
            trust_remote_code=True,
        )

        # Prepare model for training
        self.model.gradient_checkpointing_enable()

    def prepare_dataset(self) -> Dataset:
        """Prepare training dataset."""
        logger.info(f"Loading dataset from {self.dataset_path}")

        # Load and format dataset
        tool_dataset = ToolControlDataset(
            self.dataset_path, self.tokenizer, self.max_length
        )

        # Convert to HuggingFace format
        hf_dataset = tool_dataset.to_hf_dataset()

        # Split into train/validation (90/10)
        train_val_split = hf_dataset.train_test_split(test_size=0.1, seed=42)

        logger.info(f"Training examples: {len(train_val_split['train'])}")
        logger.info(f"Validation examples: {len(train_val_split['test'])}")

        return train_val_split["train"], train_val_split["test"]

    def train(self):
        """Fine-tune the tiny tool control model."""
        logger.info("Starting tool control model training...")

        # Prepare datasets
        train_dataset, val_dataset = self.prepare_dataset()

        # Training arguments optimized for speed and efficiency
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            # Training hyperparameters
            num_train_epochs=3,
            per_device_train_batch_size=4,  # Small batch for memory
            per_device_eval_batch_size=4,
            gradient_accumulation_steps=4,  # Effective batch size = 16
            # Learning rate
            learning_rate=2e-5,
            weight_decay=0.01,
            warmup_steps=100,
            # Evaluation and saving
            eval_strategy="steps",
            eval_steps=250,
            save_strategy="steps",
            save_steps=500,
            save_total_limit=3,
            # Logging
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=50,
            report_to=None,  # Disable wandb/tensorboard for now
            # Memory optimization
            dataloader_pin_memory=False,
            gradient_checkpointing=True,
            fp16=True,  # Mixed precision training
            # Early stopping
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal LM, not masked LM
        )

        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )

        # Train the model
        logger.info("Starting training...")
        trainer.train()

        # Save the final model
        logger.info(f"Saving model to {self.output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(self.output_dir)

        # Save training metrics
        metrics_file = Path(self.output_dir) / "training_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(trainer.state.log_history, f, indent=2)

        logger.info("Training completed!")

    def quantize_model(self, quantization_type: str = "Q4_K_M"):
        """Quantize the trained model for ultra-fast inference."""
        logger.info(f"Quantizing model with {quantization_type}...")

        # This would typically use tools like:
        # - llama.cpp for GGUF quantization
        # - ONNX Runtime for ONNX quantization
        # - TensorRT for NVIDIA optimization

        # For now, save instructions for manual quantization
        quantization_instructions = f"""
# Quantization Instructions for Tiny Tool Controller

## Using llama.cpp (Recommended for CPU inference):

1. Convert to GGUF format:
```bash
python convert.py {self.output_dir} --outtype f16 --outfile tiny_tool_controller.gguf
```

2. Quantize to {quantization_type}:
```bash
./quantize tiny_tool_controller.gguf tiny_tool_controller_{quantization_type.lower()}.gguf {quantization_type}
```

## Expected Performance:
- Model size: ~500MB-1GB (depending on quantization)
- Inference time: <100ms on modern CPUs
- Memory usage: <2GB RAM

## Integration with Application Controller:
```python
from llama_cpp import Llama

class TinyToolController:
    def __init__(self):
        self.model = Llama(
            model_path="models/tiny_tool_controller_{quantization_type.lower()}.gguf",
            n_ctx=512,
            n_threads=4,
            verbose=False
        )
    
    async def classify_tools(self, user_input: str) -> dict:
        prompt = f'''<|system|>You are a lightning-fast tool classifier. Analyze the user input and output the tool classification in JSON format.<|end|>
<|user|>{{user_input}}<|end|>
<|assistant|>'''
        
        response = self.model(
            prompt,
            max_tokens=200,
            temperature=0.1,
            stop=["<|end|>"]
        )
        
        return json.loads(response['choices'][0]['text'])
```
"""

        instructions_file = Path(self.output_dir) / "quantization_instructions.md"
        with open(instructions_file, "w") as f:
            f.write(quantization_instructions)

        logger.info(f"Quantization instructions saved to {instructions_file}")


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Fine-tune tiny tool control model")
    parser.add_argument(
        "--model",
        default="microsoft/Phi-3-mini-4k-instruct",
        help="Base model to fine-tune",
    )
    parser.add_argument(
        "--dataset",
        default="fine_tuning/datasets/tool_control/tool_control_training.jsonl",
        help="Path to training dataset",
    )
    parser.add_argument(
        "--output",
        default="models/tiny_tool_controller",
        help="Output directory for trained model",
    )
    parser.add_argument(
        "--max_length", type=int, default=512, help="Maximum sequence length"
    )
    parser.add_argument(
        "--quantize",
        action="store_true",
        help="Generate quantization instructions after training",
    )

    args = parser.parse_args()

    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    if device == "cpu":
        logger.warning("CUDA not available. Training will be slow on CPU.")

    # Initialize trainer
    trainer = TinyToolControlTrainer(
        model_name=args.model,
        dataset_path=args.dataset,
        output_dir=args.output,
        max_length=args.max_length,
    )

    # Train the model
    trainer.train()

    # Generate quantization instructions
    if args.quantize:
        trainer.quantize_model()

    logger.info("All done! Ready for tool control integration.")


if __name__ == "__main__":
    main()
