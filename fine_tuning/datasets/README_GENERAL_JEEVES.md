# General Phi3 ("Jeeves Base") Dataset Schema

Goal: Provide a broad, neutral assistant tuning layer (no specialization) for Phi3.

## JSONL Record Schema
Each line: a JSON object with one of the accepted field pairs.

Preferred:
```jsonc
{
  "instruction": "User instruction/question...",
  "response": "Ideal assistant response..."
}
```

Alternate (will be normalized):
```jsonc
{
  "prompt": "Instruction...",
  "output": "Assistant response..."
}
```

Optional metadata fields (ignored for loss unless `--use-metadata` provided):
```jsonc
{
  "instruction": "...",
  "response": "...",
  "category": "general|coding|reasoning|safety|other",
  "quality": 0.0-1.0,
  "source": "curated|synthetic|human",
  "tags": ["chain_of_thought", "concise"]
}
```

## Guidelines
- Keep responses helpful, concise, truthful.
- Avoid chain-of-thought unless essential; prefer summarized reasoning.
- No private / sensitive data.
- Balance categories (coding, reasoning, everyday assistance, summarization, safety refusals, tool-use style prompts (without actual tool exec)).

## File Placement
Place the finalized dataset at (default expected path):
```
data/general/jeeves_general_dataset.jsonl
```

## Quality Checklist
- [ ] Deduplicated (see `make dedupe-%` target)
- [ ] No responses exceeding 2048 tokens (truncate or refine)
- [ ] Balanced refusal examples for disallowed content
- [ ] No personally identifying information
- [ ] Consistent tonal style (professional, neutral, friendly)

## Next Steps
Once dataset is present, run:
```
make finetune-phi3-general DATASET=data/general/jeeves_general_dataset.jsonl
```
Outputs: `models/ollama_general_phi3/` (LoRA adapter + merged model optional)

---
Update this file if schema evolves.
