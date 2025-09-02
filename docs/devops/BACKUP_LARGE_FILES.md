<!-- Relocated from repository root on 2025-08-31 -->
## Large Files Removed From Git Tracking

This document lists large binary / dataset artifacts trimmed from git history. Do NOT recommit; store externally or with LFS policy once approved.

| Path | Size (approx) | Description | Suggested Retrieval Source |
|------|---------------|-------------|----------------------------|
| `data/standard/english_standard_dataset.jsonl` | ~76 MB | Instructional dataset | Internal data lake |
| `whisper/ggml-base.en.bin` | ~141 MB | Whisper base English model | Official whisper.cpp distribution |

Recovery:
```bash
mkdir -p data/standard whisper
# Place files accordingly
```

Optional LFS setup:
```bash
git lfs install
git lfs track "data/standard/english_standard_dataset.jsonl" "whisper/ggml-base.en.bin"
git add .gitattributes
```

Rationale: keep clone small; separate data/model artifacts.

Updated: 2025-08-31