# Jarvis Mix (v1) Overview

File: `mix_config_jarvis_v1.yaml`

Purpose: Define initial curated composition for Jarvis tutor / assistant fine-tuning leveraging existing processed datasets while enumerating gaps for future generation.

## Current Coverage
Pedagogy (socratic, methodology, drill-down, session management) plus reasoning math (gsm8k, OpenOrca reasoning slices, basic math, hybrid methodology+math) and interruption / recovery robustness sets.

## Gap Buckets
Marked with `gap: true` in manifest. Require generation pipelines:
- persona_stylistic_variants (style transforms over base neutral turns)
- motivational_encouragement (short affective feedback turns)
- reflective_meta_cognition (prompting learner reflection)
- safety_moderation_interventions (moderation & redirection)
- refusal_boundary_cases (edge refusal rationales)
- hallucination_grounding_checks (clarify instead of fabricate)
- adaptive_difficulty_planning (state assess + next activity plan)
- misconception_correction (misconception identification & correction dialogue)
- assessment_item_generation (question+answer+rationale artifacts)

## Implementation Guidance
A future builder script (e.g. `scripts/build_jarvis_mix.py`) should:
1. Parse manifest.
2. For each non-gap bucket: load source_files, normalize, sample per policy.
3. Enrich / validate required_meta_fields (allow legacy pass-through if `allow_legacy_rows_without_artifacts`).
4. Compute deterministic content_hash for sampling reproducibility.
5. Aggregate, enforce group proportions (or record drift if gaps disabled), output stats & manifest snapshot.

## Sampling Determinism
Use sha256(content_hash) modulo logic with `sample_seed` to keep stable subsets across revisions.

## Safety Note
Safety share is currently projected; until safety buckets are materialized, overall distribution under-represents refusal / moderation behaviors. Prioritize generating those sets early to avoid overfitting on purely didactic content.

## Next Steps
- Implement builder script & tests for sampling logic.
- Author generation notebooks / scripts for each gap bucket (store prototypes in `inbox/` then promote).
- Add CI validation step ensuring manifest sums and meta field coverage thresholds.
