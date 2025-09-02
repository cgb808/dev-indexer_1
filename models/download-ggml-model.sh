#!/usr/bin/env bash
# Minimal model download helper (whisper.cpp style) for English base model variants.
# Usage: ./models/download-ggml-model.sh base.en
# Will place models under models/whisper/
set -euo pipefail
MODEL=${1:-}
if [ -z "$MODEL" ]; then
  echo "Usage: $0 <model_name> (e.g. base.en, small.en)" >&2
  exit 1
fi
mkdir -p whisper
cd whisper
# Map model name to URL (ggml legacy). Adjust if you want gguf newer files.
BASE_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
FILE="ggml-${MODEL}.bin"
if [ -f "$FILE" ]; then
  echo "Already have $FILE" >&2
  exit 0
fi
echo "Downloading $FILE ..." >&2
curl -L -o "$FILE" "${BASE_URL}/${FILE}?download=1"
ls -lh "$FILE"
echo "Done." >&2
