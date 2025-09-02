# ZenGlow Multi-Root / Multi-Repo Workspace & Remote CUDA Dev Guide

This document unifies how to work across:

1. The primary development repo (`dev-indexer_1` – FastAPI indexer, agents, RAG,
   services) – typically developed locally (non‑CUDA) for rapid iteration.
2. A secondary curated repo (`AIWorkspace`) that receives a filtered subset of
   files for sharing, experimentation, or downstream packaging.
3. A remote GPU host (e.g. `beast3`) that provides CUDA resources for model
   training, fine‑tuning, embeddings, and heavy compute workflows.

Existing detailed docs (do not duplicate – read as needed):

- `CUDA_REMOTE_GUIDE.md` – Full remote CUDA command usage & aliases
- `FILE_TRANSFER_README.md` – File sync & mounting mechanics (`sync.sh`,
  `quick_sync.sh`)
- `repo_sync_manifest.txt` – Declarative include/exclude list for curated
  multi‑repo sync

This guide stitches them together and clarifies day‑to‑day workflows.

---

## 1. Conceptual Overview

| Concern        | Local (Non-CUDA)                                 | Remote GPU Host                                         | AIWorkspace Repo                                |
| -------------- | ------------------------------------------------ | ------------------------------------------------------- | ----------------------------------------------- |
| Purpose        | API, indexing, orchestration, light R&D          | Training, fine‑tuning, embedding generation, heavy jobs | Curated subset for distribution / collaboration |
| Python Env     | `requirements.txt` / `requirements-dev.txt`      | CUDA-enabled env (Torch, etc.)                          | Mirrors only selected files                     |
| Access Method  | Open folder normally or via multi-root workspace | `remote_cuda.sh` / VS Code Remote SSH                   | Same VS Code workspace multi-root               |
| Sync Mechanism | Source of truth                                  | `sync.sh` (push/pull/mount)                             | `multi_repo_sync.sh` (manifest-driven)          |

---

## 2. Multi-Root VS Code Workspace

File: `dev-multiroot.code-workspace`

Contains two folders:

- `dev-indexer_1` (.)
- `AIWorkspace` (../AIWorkspace)

Environment variable export inside that workspace sets `AIWORKSHOP_PATH` so
scripts (like `multi_repo_sync.sh`) know where to push.

### Opening

1. Clone / place both repositories as siblings:
   ```
   parent/
     ZenGlow/dev-indexer_1 (this repo)
     ZenGlow/AIWorkspace   (secondary curated repo)
   ```
2. Open `dev-multiroot.code-workspace` in VS Code.
3. Confirm bottom status bar shows both folders.

---

## 3. Environments & Requirements

Local (CPU / light GPU optional):

- Install base deps: `pip install -r requirements.txt`
- For development & tooling: `pip install -r requirements-dev.txt`

Remote CUDA (GPU host):

- Mirror repo structure (via `./sync.sh setup && ./sync.sh push`).
- Install training / embedding deps: `pip install -r requirements-train.txt` or
  `requirements-embed.txt` as needed.
- Optionally create a dedicated conda env (see alias `setup_conda` in
  `cuda_aliases.sh`).

Separate requirement files exist so you only install what’s needed per context.

---

## 4. File & Repo Synchronization

### 4.1 Local ↔ Remote GPU (Full Dev Tree)

Tooling:

- `sync.sh` – Structured operations (`check`, `push`, `pull`, `sync`, `mount`,
  `status`).
- `quick_sync.sh` – Aliases (`zpush`, `zpull`, `zsync`, `zmount`, `zstatus`).

Typical Flow (edit locally → run on GPU):

```bash
zpush               # or ./sync.sh push
cudapy script.py    # executes remotely via CUDA alias after sync
```

For iterative experimentation: use `zmount` to mount remote and run directly
there with remote interpreter.

### 4.2 Primary Repo → AIWorkspace (Curated Subset)

Tooling:

- `multi_repo_sync.sh` + `repo_sync_manifest.txt`

Key Idea: Start from “exclude everything”, then re-include explicit stable /
sharable paths. This prevents large artifacts or transient caches from polluting
the secondary repo.

Examples:

```bash
AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh plan   # Dry run
ALLOW_DELETE=1 AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh push
```

Add new docs/code? Update `repo_sync_manifest.txt` with the path (see Section 11
below).

---

## 5. Remote CUDA Execution Paths

Scripts:

- `remote_cuda.sh` – Full feature (check, run, python, train, jupyter, tunnel,
  monitor, info, shell, vscode)
- `remote_cuda_simple.sh` – Minimal variant
- `cuda_aliases.sh` – Quality-of-life aliases (`cudacheck`, `cudapy`,
  `cudatrain`, `cudamonitor`, etc.)

Quick Start:

```bash
source cuda_aliases.sh
cudacheck
cudatest
cudatrain train.py --epochs 5
```

Use `monitor` (`cudamonitor`) for real-time GPU utilization.

---

## 6. Workflows

### 6.1 Local API / Service Iteration (No GPU)

1. Run tests / lint: use VS Code tasks (`validate: all`).
2. Launch FastAPI dev server (`app: dev (uvicorn)` task) – purely CPU; fast
   reload cycle.
3. Commit changes; optionally sync curated subset to AIWorkspace.

### 6.2 Remote GPU Training

1. Edit training code locally.
2. `zpush` (or mount & edit directly remote if latency acceptable).
3. `cudatrain train_model.py --epochs 20`.
4. Tunnel dashboards: `cudatunnel 6006 6006 tensorboard`.
5. Long runs: use `nohup`, `tmux`, or background training pattern (see
   `CUDA_REMOTE_GUIDE.md`).

### 6.3 Embedding Generation / RAG Updates

1. Implement embedding pipeline locally.
2. Push to remote & run with `cudapy embeddings/generate_batch.py`.
3. Pull resulting vector indexes or store them in a remote vector DB (e.g.
   Chroma) accessible to local API.

### 6.4 Curated Repo Update

1. Confirm manifest includes newly relevant paths.
2. Run `./multi_repo_sync.sh plan` & review diff.
3. Run `./multi_repo_sync.sh push` (include `ALLOW_DELETE=1` only if you intend
   mirror deletions).
4. Commit changes inside AIWorkspace repo.

---

## 7. VS Code Remote Development Option

Instead of syncing-and-running, connect directly:

1. Install Remote SSH extension.
2. Connect to host (`beast3`).
3. Open `/home/<user>/ZenGlow` folder.
4. Use full IDE features with remote Python environment + GPU access.

Hybrid Pattern: Keep multi-root local window PLUS a separate remote window for
deep training tasks.

---

## 8. Environment Variable & Config Touchpoints

| Variable          | Source                                 | Purpose                           |
| ----------------- | -------------------------------------- | --------------------------------- |
| `AIWORKSHOP_PATH` | Multi-root workspace / terminal env    | Destination path for curated sync |
| SSH Host/User     | Scripts (`remote_cuda*.sh`, `sync.sh`) | Remote execution & rsync          |

Adjust remote host name or user centrally inside the scripts if infrastructure
changes.

---

## 9. Security & Separation Principles

Principle of minimal propagation: Only stable, sanitized artifacts reach
AIWorkspace; large datasets, models, caches remain in primary repo or remote
host.

Remote execution relies on SSH key auth (no passwords). Avoid embedding
credentials in scripts; prefer environment variables or a secrets manager (TBD
if/when needed).

---

## 10. Troubleshooting Matrix

| Symptom                           | Likely Cause                      | Quick Check                      | Remedy                                  |
| --------------------------------- | --------------------------------- | -------------------------------- | --------------------------------------- |
| `cudacheck` fails                 | SSH unreachable                   | `ssh user@host`                  | Fix network / SSH config                |
| `cudatest` shows CUDA unavailable | Driver / CUDA mismatch            | `nvidia-smi` remote              | Reinstall / correct driver toolkit      |
| New doc not in AIWorkspace        | Missing manifest entry            | Inspect `repo_sync_manifest.txt` | Add path under `[includes]`             |
| Slow sync                         | Large files or many small changes | `rsync -ain` dry run             | Exclude or mount instead                |
| Tunnel not opening                | Port in use locally               | `lsof -i :PORT`                  | Pick alternate local port               |
| GPU OOM                           | Batch too large                   | Training logs                    | Reduce batch size / gradient accumulate |

---

## 11. Adding New Shared Material

When you add a file or directory you want reflected in AIWorkspace:

1. Edit `repo_sync_manifest.txt` → `[includes]` section.
2. Run `./multi_repo_sync.sh plan` (verify it appears).
3. Run `./multi_repo_sync.sh push`.

Do NOT add large binary artifacts (models, datasets). Instead document retrieval
steps.

---

## 12. Quick Command Cheat Sheet

Local Dev:

```bash
pytest -q
ruff check .
uvicorn app.main:app --reload
```

Remote GPU:

```bash
source cuda_aliases.sh
zpush && cudapy script.py
cudatrain train.py --epochs 10
cudamonitor
```

Curated Sync:

```bash
./multi_repo_sync.sh plan
ALLOW_DELETE=1 ./multi_repo_sync.sh push
```

Mount Remote:

```bash
zmount   # then work under ~/remote_zenglow
```

---

## 13. Future Enhancements (Planned / Not Yet Implemented)

- Automated embedding pipeline orchestration bridging local indexer & remote GPU
- Observability / metrics standardization across local & remote (Prometheus /
  OpenTelemetry)
- Auth & secret management unification
- Production Docker image (CPU vs GPU variants)

---

## 14. Minimal Onboarding Checklist

1. Clone repos & open `dev-multiroot.code-workspace`.
2. Create local Python venv; install `requirements-dev.txt`.
3. Source `cuda_aliases.sh` (when using GPU flows).
4. `./sync.sh check && ./sync.sh push` (first remote sync).
5. `cudacheck` / `cudatest` to validate CUDA path.
6. Run local API tests & server.
7. Run a sample remote training:
   `cudatrain fine_tuning/examples/minimal_train.py` (adjust path if exists).
8. Update curated repo: `./multi_repo_sync.sh plan` then `push`.

---

## 15. Reference Index

| File                           | Purpose                                         |
| ------------------------------ | ----------------------------------------------- |
| `CUDA_REMOTE_GUIDE.md`         | Detailed remote GPU usage & alias catalog       |
| `FILE_TRANSFER_README.md`      | Sync, mount, single file operations, watch mode |
| `repo_sync_manifest.txt`       | Declarative curated sync spec                   |
| `multi_repo_sync.sh`           | Implements manifest-driven curated sync         |
| `remote_cuda.sh`               | Full-feature remote execution wrapper           |
| `remote_cuda_simple.sh`        | Minimal remote executor                         |
| `cuda_aliases.sh`              | Shell aliases & helper functions                |
| `sync.sh` / `quick_sync.sh`    | Local ↔ remote file transfer & mounting        |
| `dev-multiroot.code-workspace` | VS Code multi-root definition                   |

---

## 16. Feedback Loop

If a workflow feels repetitive or fragile:

1. Add or refine an alias (in `cuda_aliases.sh`).
2. Document the stable pattern here (avoid duplicating deep details).
3. Consider whether it belongs in curated subset → update manifest.

This document is intentionally concise yet integrative—defer to the linked
specialized docs for drill‑down procedures.

---

_Last updated: TBD (update when edited)._
