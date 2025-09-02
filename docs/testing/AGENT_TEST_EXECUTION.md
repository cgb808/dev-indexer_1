<!-- Relocated from repository root on 2025-08-30 -->
[Back to Docs Index](../../DOCS_INDEX.md)

# Agent Test Execution Guide

This repository exposes a consistent command the Copilot (or any automation agent) can invoke to run Python tests for the indexer/RAG system.

## Primary Command
Run all tests:
```
bash run_tests.sh
```
Pass additional pytest selectors / options:
```
bash run_tests.sh -k rag_query
```
Fail fast (first failure):
```
FAST=1 bash run_tests.sh
```

## Script Behavior (`run_tests.sh`)
1. Ensures a Python virtual environment at `.venv` (creates if absent).
2. Installs required dependencies and `pytest`.
3. Executes `pytest` against repository tests quietly (`-q`).
4. Propagates pytest exit code for CI / agent evaluation.

## VS Code Task
Task label: Run All Tests → invokes `bash run_tests.sh`.

## Expected Exit Codes
| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | Test failures occurred |
| >1 | Infrastructure / invocation error |

## Agent Integration Hints
| Step | Action |
|------|--------|
| Verify | `test -f run_tests.sh` |
| Dry Run | `bash run_tests.sh -k smoke || true` |
| Full | `bash run_tests.sh` and parse summary |

## Adding New Tests
Place new test modules under `tests/` using `test_*.py` naming.

## Future Enhancements
* Coverage integration
* API-triggered test run endpoint
* CI workflow automation

---
This doc is optimized for autonomous agents needing deterministic test invocation.
