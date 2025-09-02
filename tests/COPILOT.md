# 🔷 AI Terminal Co‑Pilot — Standard Operating Procedures

Table of Contents
1. Introduction
2. Core Principles
3. Modes of Operation (A: Manual • B: Autonomous)
4. Error Handling Protocol
5. Command Execution Format
6. Confirmation & Safety Matrix
7. Goal Templates
8. Sample Session (Manual)
9. Sample Session (Autonomous)
10. Revision History
11. Implementation Notes

<!-- Legend: <PRIMARY>=🔷  <ACCENT>=🟢  <WARN>=🟠  <DANGER>=🔴  <INFO>=🔹  <OK>=✅ -->

---
## 1. Introduction
These SOPs define safe, efficient collaboration with the AI terminal co‑pilot. Two execution modes are supported: **Manual Step‑by‑Step** (precision) and **Autonomous Goal Execution** (speed).

---
## 2. Core Principles
**Clear Goal** – Start every session with a single concise objective.

> Vague: “I want to look at the project files.”  
> Clear: “Find Python files in `src/` modified in last 48h and zip them.”

**Provide Context** – Reference `project-index.json` for layout & dependencies.

**Safety for Destructive Ops** – Require explicit confirmation for `rm`, `mv`, resets, force pushes, DB destructive commands.

**Minimal Surface Change** – Favor smallest viable diff / command.

**Observability** – Scripts include `-h` usage help.

**Structured Directories (Root Hygiene)** – New files belong in the correct domain directory, not root. Root is limited to: `README.md`, `COPILOT.md`, `Makefile`, `docker-compose*.yml`, `kong.yml`, `package.json`, `package-lock.json`, `project-index*.json`, `requirements-*.txt`, `settings.json`, `pytest.ini`, `run_tests.sh`, `.env*` variants, `.gitignore` and essential config. Everything else:
- Code → `app/`, `scripts/`, `frontend/`, `sql/`, `infrastructure/`, `fine_tuning/`.
- Docs → `docs/` (core) or `documentation/` (deep narrative) – never new doc markdown at root.
- Generated artifacts → `artifact/` (subfolder) or `archive/` for deprecated.
- Data samples → `data/`.
- Tests → `tests/` (create subfolders like `tests/data/` as needed).

Reject / relocate any proposed root additions automatically unless explicitly instructed.

Automated Enforcement:
- Run `python scripts/root_hygiene_check.py` prior to committing large doc reorganizations.
- Any new root markdown outside allowlist triggers failure (pending CI integration). Keep doc additions in `docs/`.

---
## 3. Modes of Operation
### Mode A — Manual (⚙️ Precision)
1 command at a time + rationale. Use for refactors, prod-adjacent work, ambiguity.

### Mode B — Autonomous (🚀 Speed)
Expands high-level goal into a sequence; self-checks; reverts to Manual on ambiguity.

Escalate down if >1 consecutive uncertainty.

---
## 4. Error Handling Protocol (🚨)
On failure:
1. Show command, exit code, condensed stderr (first & last lines if long).
2. Diagnose (1–2 sentences root cause hypothesis).
3. Offer up to 3 fixes (safest→most invasive).
4. Await confirmation.
5. Apply / request clarification.
Repeat category failure twice → suggest fallback strategy.

---
## 5. Command Execution Format
All runnable commands inside fenced bash blocks only.
Example:
```bash
find src -name "*.py" -mtime -2 -print | sort
```
Optional ANSI:
```bash
echo -e "\033[1;34m[info]\033[0m Scanning recent Python files"
```
Avoid chaining unrelated commands with && unless atomic.

---
## 6. Confirmation & Safety Matrix
| Action Type | Examples | Needs OK |
|-------------|----------|----------|
| Read-only | ls, find, grep | No |
| Build/test | npm test, pytest | No |
| Small edit | echo > file | Maybe (critical path?) |
| Bulk rename/delete | rm -rf, mass sed | Yes |
| Git history rewrite | reset --hard, push --force | Yes |
| DB destructive | DROP TABLE, mass UPDATE | Yes |

---
## 7. Goal Templates
Manual:
`Goal: <objective>; Constraints: <time/risk/perf>; Context: <repo area>; Done when: <condition>.`

Autonomous:
```
GOAL:
<outcome>

CONTEXT:
<dirs, env, index file>

CONSTRAINTS:
- time: <limit>
- risk tolerance: <low|medium|high>

DEFINITION OF DONE:
- <bullet>
- <bullet>
```

---
## 8. Sample Session (Manual)
User goal → single command → output → iterate.
```bash
find src -type f -name "*.py" -printf '%s %p\n' | sort -nr | head -20
```

---
## 9. Sample Session (Autonomous)
Co‑pilot iterates steps; on anomaly → manual.

---
## 10. Revision History
- v1.1 (2025-08-29) Icons, tables, safety matrix
- v1.0 Initial

---
## 11. Implementation Notes
Internalize: mode heuristic, safety matrix, error protocol.

Hygiene Artifacts:
- Feature: Clarifying priority (heuristic + feature extractor) tracked in `app/rag/clarify_priority_features.py` and dataset builder `scripts/build_clarify_priority_dataset.py`.
- Root hygiene audit in `docs/ROOT_HYGIENE_AUDIT.md`.

✅ End of SOP