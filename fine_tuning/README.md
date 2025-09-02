<!-- Directory Index: fine_tuning/ -->
# fine_tuning/ Datasets & Training

Subdirectories:
- `datasets/` – Raw & processed instruction / tutoring corpora.
- `models/` – Model configs or fine-tune artifacts (planned).
- `training/` – Training scripts / orchestration.
- `validation/` – Evaluation & quality metrics.
- `tooling/` – Helper utilities.

Navigation Helper: `navigate_finetuning.py`

Related Docs:
- Project overview: `../README.md`
- (Add fine-tuning strategy doc if not yet present.)# Fine-Tuning Operations Center

## Directory Structure

### 📊 Datasets
- `datasets/raw/` - Original, unprocessed datasets
- `datasets/processed/` - Cleaned and formatted datasets  
- `datasets/splits/` - Train/validation/test splits
- `datasets/manifests/` - Dataset metadata and statistics

### 🤖 Models
- `models/base/` - Original base models (phi3, mistral, etc)
- `models/checkpoints/` - Training checkpoints and intermediate saves
- `models/fine_tuned/` - Completed fine-tuned models
- `models/configs/` - Model configuration files

### 🚀 Training
- `training/scripts/` - Training and fine-tuning scripts
- `training/configs/` - Training configuration files
- `training/logs/` - Training logs and metrics
- `training/experiments/` - Experimental training runs

### ✅ Validation
- `validation/scripts/` - Model validation and testing scripts
- `validation/results/` - Validation results and comparisons
- `validation/benchmarks/` - Benchmark tests and scores

### 🛠️ Tooling
- `tooling/rag/` - RAG integration tools and scripts
- `tooling/audio/` - TTS/STT and audio processing tools
- `tooling/visual/` - Visualization and diagram generation
- `tooling/coordination/` - Multi-model coordination scripts

## Quick Start Commands

```bash
# Start training environment
cd fine_tuning/training/scripts
python hybrid_model_trainer.py

# Run validation tests
cd fine_tuning/validation/scripts
python ultimate_models_comparison.py

# Check dataset statistics
cd fine_tuning/datasets/manifests
cat latest_dataset_stats.json
```

## Current Status
- ✅ Hybrid methodology proven (46-point winner)
- ✅ 8-epoch calculative strategy established  
- ✅ 1,842 examples in balanced dataset
- 🔄 Personality integration in progress
- 🔄 Multi-model coordination development
