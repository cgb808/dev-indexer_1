# Multi-Repo / Multi-Root Workspace Setup

This guide wires the local `dev-indexer_1` workspace together with the curated
remote-oriented `AIWorkspace` repo while keeping large data and transient
artifacts isolated.

## Goals

- Develop core code once; publish subsets to a remote-focused repo.
- Avoid duplicating large `data/` or `artifact/` trees.
- Enable side‑by‑side editing (multi-root VS Code workspace).
- Support manifest‑driven selective sync both directions.

## Components

| File                                 | Purpose                                     |
| ------------------------------------ | ------------------------------------------- |
| `multi_repo_sync.sh`                 | Selective rsync push/pull based on manifest |
| `repo_sync_manifest.txt`             | General curated subset (AIWorkshop style)   |
| `repo_sync_manifest_aiworkspace.txt` | Remote/CUDA focused subset                  |
| `dev-multiroot.code-workspace`       | VS Code multi-root workspace definition     |

## Clone Layout (Assumed)

```
.../ZenGlow/
  dev-indexer_1/        (this repo)
  AIWorkspace/          (git@github.com:cgb808/AIWorkspace.git)
```

Clone second repo:

```bash
cd /mnt/DevBuilds/ZenGlow/ZenGlow
git clone git@github.com:cgb808/AIWorkspace.git
cd AIWorkspace
git checkout main   # or desired branch
```

## Open Multi-Root Workspace

In VS Code: File > Open Workspace from File... select
`dev-indexer_1/dev-multiroot.code-workspace`.

Environment variable `AIWORKSHOP_PATH` is auto-injected (points to the second
root) enabling:

```bash
./multi_repo_sync.sh --dest "$AIWORKSHOP_PATH" plan
```

## Common Workflows

Dry-run what would sync (default manifest):

```bash
AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh plan
```

Use alternate manifest optimized for remote (CUDA) code:

```bash
AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh --manifest repo_sync_manifest_aiworkspace.txt plan
```

Push curated subset (no deletions by default):

```bash
AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh push
```

Mirror deletions too:

```bash
ALLOW_DELETE=1 AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh push
```

Pull changes back (careful—overwrites included subset):

```bash
AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh pull
```

Inspect differences quickly:

```bash
AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh diff
```

Status snapshot:

```bash
AIWORKSHOP_PATH=../AIWorkspace ./multi_repo_sync.sh status
```

## Git Remote Alternative (Optional)

Instead of a second working copy you can add a _second remote_ to this repo:

```bash
git remote add aiworkspace git@github.com:cgb808/AIWorkspace.git
git fetch aiworkspace
```

Then use a sparse commit strategy (e.g., subdirectory filter or
`git subtree`)—but this couples histories and is harder to keep clean. The
two‑clone + rsync manifest approach is simpler and safer for asymmetric content.

## Safety / Gotchas

- `ALLOW_DELETE=1` will remove files at destination not in the curated
  set—double check with `plan` first.
- Large directories (`data/`, `artifact/`) are excluded—sampling handled via
  `remote_data.sh` directly on the remote host.
- Always commit / stash local changes in both roots before running `pull` to
  avoid overwrites.

## Next Enhancements (Future)

- Add checksum manifest for integrity verification.
- Pre-commit hook to warn if modifying excluded large paths.
- CI job in AIWorkspace to validate subset builds independently.

---

Maintained by multi-repo tooling. Update this doc as manifests evolve.
