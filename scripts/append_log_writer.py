#!/usr/bin/env python3
"""Append Log Writer for Streaming Conversation Events

Writes length-prefixed MessagePack frames to per-session log files for low-lock
multi-session input. Rotation criteria (size/time) triggers closure and queueing.

Rotation queue: pushes sealed segment path onto Redis list (if configured) or prints path.

Frame schema:
  {
    "version":1,
    "time": iso8601,
    "session_id": str(UUID),
    "user_id": str,
    "role": "user|assistant|system",
    "seq": int,
    "content": text,
    "metadata": { tokens:int?, tags:[], ... }
  }
"""
from __future__ import annotations
import argparse, os, sys, time, json, uuid, struct, re
from datetime import datetime, UTC
from pathlib import Path

try:
    import msgpack  # type: ignore
except Exception as e:  # noqa: BLE001
    print("msgpack required", e, file=sys.stderr); raise

def iso() -> str:
    return datetime.now(UTC).isoformat()

SAFE_SESSION_RE = re.compile(r'[^A-Za-z0-9._-]+')

def sanitize_session_id(raw: str) -> str:
    """Reduce session id to safe filename component.
    Collapses disallowed characters to hyphen; trims length.
    """
    # Preserve uuid-like portion if present
    cleaned = SAFE_SESSION_RE.sub('-', raw).strip('-') or 'session'
    return cleaned[:120]

def open_log(base_dir: Path, session_id: str) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"session_{session_id}.logtmp"

def seal_log(path: Path) -> Path:
    final = path.with_suffix('.log')
    path.rename(final)
    return final

def queue_segment(seg: Path, redis_list: str|None) -> bool:
    """Queue sealed segment path. Returns True on success / local fallback.
    False only if an explicit redis push was requested and failed.
    """
    if redis_list:
        try:
            import redis  # type: ignore
            r = redis.from_url(os.getenv('REDIS_URL','redis://localhost:6379/0'))
            r.lpush(redis_list, str(seg))
            print(f"[queue] {seg} -> {redis_list}")
            return True
        except Exception as e:  # noqa: BLE001
            print(f"[queue] redis fail: {e}")
            return False
    print(f"[segment] sealed {seg}")
    return True

def write_frame(fh, obj, do_fsync: bool = False):
    payload = msgpack.packb(obj, use_bin_type=True)
    fh.write(struct.pack('>I', len(payload)))
    fh.write(payload)
    if do_fsync:
        fh.flush()
        os.fsync(fh.fileno())

def discover_last_seq(path: Path) -> int:
    """Scan existing logtmp for last seq number; returns -1 if none.
    Optimistic forward scan (length-prefixed frames). If corruption encountered,
    stops and returns last good seq.
    """
    if not path.exists() or path.stat().st_size == 0:
        return -1
    last = -1
    try:
        with open(path, 'rb') as fh:
            while True:
                hdr = fh.read(4)
                if len(hdr) < 4:
                    break
                (length,) = struct.unpack('>I', hdr)
                payload = fh.read(length)
                if len(payload) < length:
                    break  # truncated
                try:
                    frame = msgpack.unpackb(payload, raw=False)
                    seq_val = frame.get('seq')
                    if isinstance(seq_val, int):
                        last = seq_val
                except Exception:  # noqa: BLE001
                    break
    except Exception as e:  # noqa: BLE001
        print(f"[warn] seq scan failed: {e}")
    return last

def main():
    ap = argparse.ArgumentParser(description="Append log writer (stream events)")
    ap.add_argument('--session-id', default=str(uuid.uuid4()))
    ap.add_argument('--user-id', required=True)
    ap.add_argument('--role', default='user')
    ap.add_argument('--content', required=True)
    ap.add_argument('--log-dir', default='data/append_logs')
    ap.add_argument('--max-size', type=int, default=64*1024*1024)
    ap.add_argument('--max-age', type=int, default=600, help='seconds')
    ap.add_argument('--redis-list')
    ap.add_argument('--strict-queue', action='store_true', help='Exit non-zero if queue push fails')
    ap.add_argument('--metadata-json')
    ap.add_argument('--seq', type=int)
    ap.add_argument('--auto-seq', action='store_true', help='If --seq omitted, auto-increment based on existing log')
    ap.add_argument('--fsync', action='store_true', help='fsync after each append for durability')
    args = ap.parse_args()
    session_id = sanitize_session_id(args.session_id)
    log_dir = Path(args.log_dir)
    log_path = open_log(log_dir, session_id)
    # rotation check
    created = log_path.stat().st_mtime if log_path.exists() else time.time()
    rotate = False
    if log_path.exists() and log_path.stat().st_size >= args.max_size:
        rotate = True
    if time.time() - created >= args.max_age:
        rotate = True
    if rotate and log_path.exists():
        sealed = seal_log(log_path)
        ok = queue_segment(sealed, args.redis_list)
        if args.strict_queue and not ok:
            print('[error] queue push failed (strict mode)', file=sys.stderr)
            sys.exit(2)
        # open a new temp
        log_path = open_log(log_dir, session_id)
    if args.metadata_json:
        try:
            meta = json.loads(args.metadata_json)
            if not isinstance(meta, dict):
                raise ValueError('metadata must be object')
        except Exception as e:  # noqa: BLE001
            print(f"[warn] bad metadata JSON: {e}; using empty object")
            meta = {}
    else:
        meta = {}
    seq = args.seq
    if seq is None and args.auto_seq:
        seq = discover_last_seq(log_path) + 1
    frame = {
        'version':1,
        'time': iso(),
        'session_id': session_id,
        'user_id': args.user_id,
        'role': args.role,
        'seq': seq,
        'content': args.content,
        'metadata': meta,
    }
    with open(log_path, 'ab') as fh:
        write_frame(fh, frame, do_fsync=args.fsync)
    print(f"[append] {session_id} size={log_path.stat().st_size} seq={frame['seq']}")

if __name__=='__main__':
    main()
