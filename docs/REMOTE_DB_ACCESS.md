## Remote / Secure Access to Postgres (pgvector + Timescale)

This service ships a Postgres instance (pgvector image). Directly exposing `5432` on all interfaces is discouraged. Preferred patterns:

### 1. SSH Local Port Forward (Most Common / Fast)
Forward local port 5433 on your laptop → remote host container port 5432 (bound to 127.0.0.1 on host):

```bash
ssh -N -L 5433:127.0.0.1:5432 cgb808@<beast-host>
# Then connect locally:
psql postgresql://postgres:your-super-strong-and-secret-password@127.0.0.1:5433/rag_db
```

Background (auto-close on disconnect):
```bash
ssh -f -N -L 5433:127.0.0.1:5432 cgb808@<beast-host>
```

### 2. SSH Reverse Tunnel (If You Cannot Initiate From Client Side)
From DB host (beast) back to a reachable workstation:
```bash
ssh -R 15432:127.0.0.1:5432 user@workstation.example
```
Workstation then connects to `localhost:15432`.

### 3. Autossh (Persistent Tunnels)
Install `autossh` on client:
```bash
autossh -M 0 -f -N -L 5433:127.0.0.1:5432 cgb808@<beast-host>
```

### 4. WireGuard / Tailscale (Overlay Network)
Create a private network so the DB host has a stable tailnet IP (e.g., 100.x.y.z) and keep Postgres bound to `127.0.0.1` while exposing an internal SSH for tunneling. Optionally you can bind Postgres to the WireGuard interface only (e.g. `listen_addresses = '127.0.0.1, wg0'`).

### 5. API-Level Access (RAG Endpoints Instead of SQL)
For most consumers, prefer calling the FastAPI endpoints (`/rag/query`, `/rag/ingest`, `/model/embed`) rather than granting raw SQL. This reduces:
* Attack surface (no ad-hoc SQL)
* Coupling to schema changes
* Risk of accidental destructive queries

### 6. Read-Only Role for Analytics
Create a limited user for analysts:
```sql
CREATE ROLE rag_read LOGIN PASSWORD 'change-me';
GRANT CONNECT ON DATABASE rag_db TO rag_read;
GRANT USAGE ON SCHEMA public TO rag_read;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rag_read;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO rag_read;
```
Use this user in tunnels: `postgresql://rag_read:change-me@127.0.0.1:5433/rag_db`.

### 7. Enabling TLS (Optional Hardening)
For pure SSH tunnel usage TLS is not mandatory (traffic already encrypted). If you must expose Postgres beyond SSH/VPN, configure server certs:
1. Generate key/cert under `./pgdata` (owned by postgres).
2. Set in `postgresql.conf`:
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```
3. Restart container.

### 8. pg_hba.conf Hardened Entries
Append (or ensure) lines restricting local loopback + TLS only if later exposed:
```
host    all  all  127.0.0.1/32        scram-sha-256
hostssl all  all  10.0.0.0/24         scram-sha-256
```

### 9. Avoid Direct Wide Exposure
Do NOT publish `0.0.0.0:5432` unless behind firewall rules. Current compose binds to `127.0.0.1:5432` intentionally.

### 10. Quick Helper Script
See `scripts/db_ssh_tunnel.sh` for a wrapper.

---
Choose: Use (1) for ad-hoc, (3) for persistent, (4) for team networks, (5) for application consumption.
