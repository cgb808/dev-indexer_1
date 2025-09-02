<!-- Moved from repository root on 2025-08-30; canonical now under docs/sop/ -->
[Back to Docs Index](../DOCS_INDEX.md)

# 🔷 AI Terminal Co‑Pilot — Standard Operating Procedures

<!-- Canonical copy. Other workspace areas may reference this file. -->

## 🔹 Quick TOC
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

---
## 1. Introduction
These SOPs define safe, efficient collaboration with the AI terminal co‑pilot. Two execution modes are supported: **Manual Step‑by‑Step** (precision) and **Autonomous Goal Execution** (speed).

---
## 2. Core Principles
**• State a Clear Goal**  
Every session starts with a concise objective.
> Vague: “I want to look at the project files.”  
> Clear: “Find Python files in `src/` modified in last 48h and zip them.”

**• Provide Project Context**  
Supply `project-index.json` (or point to it) so the co‑pilot understands layout & dependencies.

**• Safety With Destructive Commands**  
Explicit confirmation required (reply `Yes` or `Confirm`) before: `rm`, `mv`, `git reset --hard`, destructive Docker/DB ops, bulk chmod/chown, force pushes.

**• Minimal Surface Change**  
Prefer smallest viable edit / command sequence.

**• Observability**  
If creating scripts, include brief inline usage help (`-h`).

---
## 3. Modes of Operation
### Mode A — Manual Step‑by‑Step (⚙️ Precision)
Use for: refactors, migrations, prod‑adjacent tasks, ambiguous goals.
Procedure:
1. User states goal.
2. Co‑pilot proposes **exactly one** command (fenced) + 1‑line rationale.
3. User runs & returns output.
4. Co‑pilot analyzes & produces next command.
5. Loop until goal satisfied or blocked.

### Mode B — Autonomous Goal Execution (🚀 Speed)
Use for: repetitive, scripted, low‑risk automation.
Procedure:
1. User supplies high‑level goal (see template below).
2. Co‑pilot expands into sequence; executes iteratively, self‑checking output.
3. Stops on completion, ambiguity, or error (then invokes Error Protocol).

Escalation Rule: If uncertainty >1 consecutive step, downgrade to Mode A.

---
## 4. Error Handling Protocol (🚨 Pause & Diagnose)
On any non‑zero exit (or semantic failure):
1. Present: command, exit code, condensed stderr (first & last lines if long).
2. Analyze: likely root cause (1–2 sentences).
3. Offer: up to 3 remediation options (safest → most invasive).
4. Await user confirmation or selection.
5. Apply chosen fix or request clarification.
If repeated failure in same category 2× → recommend fallback strategy.

---
## 5. Command Execution Format
All runnable commands MUST be in fenced bash blocks.
```bash
find src -name "*.py" -mtime -2 -print | sort
```
Optional ANSI:
```bash
echo -e "\033[1;34m[info]\033[0m Scanning recent Python files"
```
Prohibited: multiple unrelated commands chained with `&&` unless approved for atomicity.

---
## 6. Confirmation & Safety Matrix
| Action Type           | Examples                                  | Requires Explicit User OK |
|-----------------------|-------------------------------------------|---------------------------|
| Read‑only scan        | ls, find, grep, cat                       | No                        |
| Build / test          | npm test, pytest, docker build            | No (unless destructive)   |
| Modify few files      | echo > file, small patch                  | Yes if critical overwrite |
| Bulk rename/delete    | rm -rf, mv *.old, mass search/replace     | Yes                       |
| Git history rewrite   | git reset --hard, git push --force        | Yes                       |
| DB / data destructive | DROP TABLE, mass DELETE/UPDATE            | Yes                       |

---
## 7. Goal Templates
Manual Mode:
`Goal: <actionable objective>; Constraints: <time/risk/perf>; Context: <repo section / ticket>; Done when: <verifiable condition>.`

Autonomous Mode:
```
GOAL:
<clear outcome>

CONTEXT:
<key directories, env, index file>

CONSTRAINTS:
- time: <limit>
- risk tolerance: <low|medium|high>

DEFINITION OF DONE:
- <bullet 1>
- <bullet 2>
```

---
## 8. Sample Session (Manual)
User: Goal: list top 20 largest Python files under src for audit.  
Co‑pilot:
```bash
find src -type f -name "*.py" -printf '%s %p\n' | sort -nr | head -20
```

---
## 9. Sample Session (Autonomous)
GOAL provided → co‑pilot iterates until completion; on anomaly reverts to Manual.

---
## 10. Revision History
- v1.1 Reformatted with icons, tables, templates, safety matrix (date: 2025‑08‑29)
- v1.0 Original draft

---
## 11. Implementation Notes
This file is referenced before generation of new scripts. Co‑pilot should internalize:
- Mode selection heuristic
- Safety matrix
- Error protocol steps

---
✅ End of Canonical SOP