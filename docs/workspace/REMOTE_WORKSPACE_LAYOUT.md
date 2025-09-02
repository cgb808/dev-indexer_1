<!-- Relocated from repository root on 2025-08-30 -->
[Back to Docs Index](../../DOCS_INDEX.md)

# Remote Workspace Optimal Layout

```
dev-indexer_1/
  app/
    main.py
    core/
    rag/
    health/
  scripts/
  sql/
  docs/
  tests/
  data_sources/
  test_data/
  requirements.txt
  Dockerfile
  docker-compose.yml
```

Purpose highlights:
* `core` central config & logging.
* `rag` embedding + retrieval pipeline.
* `sql` schema + migrations.
* `tests` fast regression set.
* `scripts` operational utilities.

Recommended growth: exact search → HNSW/IVF → caching → tracing/metrics → multi-tenant.
