#!/usr/bin/env bash
set -euo pipefail

# Rotate role passwords safely.
# Usage (env var driven to avoid shell history leaks):
#   export PGURL=postgresql://postgres:adminpass@127.0.0.1:5433/rag_db
#   export NEW_RAG_READ=... NEW_RAG_WRITE=... NEW_RAG_ADMIN=...
#   ./scripts/rotate_role_passwords.sh

if [[ -z "${PGURL:-}" ]]; then
  echo "Set PGURL (connection string with superuser or owner)." >&2
  exit 2
fi

psql "$PGURL" <<SQL
\set ON_ERROR_STOP on
DO \$\$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='rag_read') THEN EXECUTE 'ALTER ROLE rag_read PASSWORD ' || quote_literal('${NEW_RAG_READ:-change_me_read}'); END IF; END \$\$;
DO \$\$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='rag_write') THEN EXECUTE 'ALTER ROLE rag_write PASSWORD ' || quote_literal('${NEW_RAG_WRITE:-change_me_write}'); END IF; END \$\$;
DO \$\$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='rag_admin') THEN EXECUTE 'ALTER ROLE rag_admin PASSWORD ' || quote_literal('${NEW_RAG_ADMIN:-change_me_admin}'); END IF; END \$\$;
SQL

echo "[rotate] Done. Remember to update any stored DSNs."
