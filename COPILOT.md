# Copilot / AI Assistant Operating Brief

Authoritative, high-signal reference for automated assistance inside this repo.
Keep responses action-oriented, minimal, and grounded in CURRENT repository
facts.

## Core Domains

- FastAPI indexer & service code under `app/`
- Remote CUDA training & embeddings via `remote_cuda.sh` / `cuda_aliases.sh`
- Multi-root workspace pairing this repo with a curated subset repo
  (`AIWorkspace`)
- Curated sync mechanism (`multi_repo_sync.sh` + `repo_sync_manifest.txt`)

## Key Docs

| Doc                            | Purpose                                                  |
| ------------------------------ | -------------------------------------------------------- |
| `docs/MULTI_ROOT_WORKSPACE.md` | End-to-end multi-root, remote GPU, curated sync workflow |
| `CUDA_REMOTE_GUIDE.md`         | Detailed remote CUDA command & alias usage               |
| `FILE_TRANSFER_README.md`      | Local ↔ remote sync & mount operations                  |
| `repo_sync_manifest.txt`       | Declares curated subset (AIWorkspace) includes/excludes  |
| `multi_repo_sync.sh`           | Implements manifest-driven selective sync                |

## Golden Rules

1. Minimal Diff Principle: propose smallest viable change; batch logically
   related edits.
2. One Terminal Action per Step: never chain multiple critical commands without
   awaiting output.
3. Fact Discipline: if a detail is not in the repo or prior validated output,
   mark as unknown instead of guessing.
4. No Speculative Infra: do not introduce services, deps, or env vars until
   clearly needed.
5. Remote vs Local Boundary: heavy training/embeddings run remote (CUDA); API
   iteration stays local unless explicitly moved.
6. Curated Subset Hygiene: new share-worthy docs/code -> add to `[includes]` in
   `repo_sync_manifest.txt`.
7. Avoid Large Artifacts: never sync datasets / model weight binaries into
   curated subset.

## Common Workflows (Assistant Perspective)

| Intent                      | Sequence                                                                |
| --------------------------- | ----------------------------------------------------------------------- |
| Run tests & lint            | `pytest -q` then `ruff check .` then `mypy app`                         |
| Launch API dev server       | Use VS Code task `app: dev (uvicorn)`                                   |
| Remote training             | Ensure latest code `./sync.sh push` -> `cudatrain <script>.py ...`      |
| Add new doc to curated repo | Edit/create doc -> update manifest -> `multi_repo_sync.sh plan` -> push |
| Inspect health endpoints    | GET `/health`, `/vector/ping`                                           |

## Commit Message Guidance

Format: `<area>: <concise intent>` then short bullet list of scope /
constraints. Example:

```
docs: add multi-root + remote CUDA integration guide

- New: docs/MULTI_ROOT_WORKSPACE.md
- Updated manifest to include guide
- No code logic changes
```

## When Unsure

Explicitly request clarification ONLY if blocked after listing reasonable, safe
assumptions (≤2) and proposed next step for each.

## Red Flags to Call Out

- Introducing unpinned dependency versions that differ from existing patterns.
- Adding environment variables without documenting usage.
- Creating root-level files not in allowlist (see `settings.json` instructions)
  unless justified.
- Attempting to move heavy GPU workflows local.

## Quick Reference Aliases (from `cuda_aliases.sh`)

`cudacheck` (connection/CUDA), `cudapy` (python script), `cudatrain` (training),
`cudamonitor` (watch GPU), `cudajup` (Jupyter), `cudatunnel` (port fwd).

## Update Protocol

If you materially change workflows (new script, new doc, rename), update:

1. The specific doc (e.g. `MULTI_ROOT_WORKSPACE.md`).
2. This file (section referencing it).
3. The curated manifest if share-worthy.

---

Last updated: 2025-09-01
