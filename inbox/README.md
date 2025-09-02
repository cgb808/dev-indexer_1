# Inbox (Temporary Drop Zone)

Purpose:
- Quick place to drop ad‑hoc files, scratch scripts, raw data snippets, and one‑off experiments before they are triaged into their permanent home (e.g. `scripts/`, `data/`, `docs/`, `app/`).

Workflow:
1. Drop file here (naming convention: `<date>_<short-topic>_<purpose>.<ext>` e.g. `2025-08-31_vector_probe.py`).
2. If the artifact becomes canonical, MOVE it out to the appropriate directory.
3. Keep this directory lean; prune stale items regularly.
4. Sensitive / large (>5MB) or secrets-containing files SHOULD NOT be committed. Use `.gitignore` overrides.

Git Commit Policy:
- By default most arbitrary files are ignored (see `.gitignore`).
- Allowed by default: `*.py`, `*.md`, `*.sql`, `*.sh`, `.keep`.
- To force‑include another file type, add a targeted negation rule near the bottom of `.gitignore` OR relocate the file.

Suggested Subpatterns (optional):
- `*_scratch.py`  – exploratory scripts.
- `*_note.md`     – transient notes (convert to proper docs later).
- `raw_*`         – raw input awaiting transformation.

Retention Guidelines:
- Anything older than 30 days without updates should be reviewed and either promoted or deleted.
- No production dependencies should point into `inbox/`.

Security / Compliance:
- Do not place secrets, API keys, or proprietary customer data here.
- Use environment variables or secret managers instead of committing credentials.

Automation Ideas (future):
- A triage script to list age > N days.
- Pre-commit hook warning when committing large binaries in `inbox/`.

This file (README.md) is tracked to ensure the directory exists in source control.
