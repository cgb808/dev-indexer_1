#!/usr/bin/env python3
"""Append Log Reader / Sealed Segment Expander

Reads one or more sealed .log (or in-progress .logtmp) files produced by
append_log_writer and emits JSONL frames (optionally pretty JSON) or
MessagePack re-stream.

Features:
  * Integrity scan (stops on truncated/corrupt frame unless --lenient)
  * Output filtering by session/user/role/time range
  * Stats summary (--stats) for quick inspection
  * Detect sequence gaps
"""
from __future__ import annotations
import argparse, sys, json, struct
from pathlib import Path
from datetime import datetime

try:
    import msgpack  # type: ignore
except Exception as e:  # noqa: BLE001
    print("msgpack required", e, file=sys.stderr); raise

def read_frames(path: Path, stop_on_error: bool=True):
    with open(path, 'rb') as fh:
        offset = 0
        while True:
            hdr = fh.read(4)
            if not hdr:
                break
            if len(hdr) < 4:
                if stop_on_error:
                    print(f"[error] truncated length header at {offset}", file=sys.stderr)
                    break
                else:
                    return
            (length,) = struct.unpack('>I', hdr)
            payload = fh.read(length)
            if len(payload) < length:
                if stop_on_error:
                    print(f"[error] truncated payload at {offset}", file=sys.stderr)
                break
            try:
                frame = msgpack.unpackb(payload, raw=False)
                yield frame
            except Exception as e:  # noqa: BLE001
                if stop_on_error:
                    print(f"[error] unpack failed at {offset}: {e}", file=sys.stderr)
                    break
            offset += 4 + length

def main():
    ap = argparse.ArgumentParser(description="Read sealed append log segments")
    ap.add_argument('paths', nargs='+', help='log or logtmp files')
    ap.add_argument('--jsonl', action='store_true', help='Emit JSONL (default)')
    ap.add_argument('--pretty', action='store_true', help='Pretty JSON output')
    ap.add_argument('--msgpack', action='store_true', help='Emit raw MessagePack frames (length-prefixed)')
    ap.add_argument('--lenient', action='store_true', help='Continue on frame errors')
    ap.add_argument('--session')
    ap.add_argument('--user')
    ap.add_argument('--role')
    ap.add_argument('--since')
    ap.add_argument('--until')
    ap.add_argument('--stats', action='store_true', help='Print summary stats to stderr')
    ap.add_argument('--detect-gaps', action='store_true')
    args = ap.parse_args()

    def parse_time(ts: str):
        return datetime.fromisoformat(ts.replace('Z','+00:00'))

    since_dt = parse_time(args.since) if args.since else None
    until_dt = parse_time(args.until) if args.until else None

    total = 0
    sessions = {}
    gaps = []

    for p in args.paths:
        path = Path(p)
        last_seq = None
        for frame in read_frames(path, stop_on_error=not args.lenient):
            total += 1
            t = frame.get('time')
            dt = None
            if t:
                try:
                    dt = parse_time(t)
                except Exception:
                    pass
            if since_dt and dt and dt < since_dt:
                continue
            if until_dt and dt and dt > until_dt:
                continue
            if args.session and frame.get('session_id') != args.session:
                continue
            if args.user and frame.get('user_id') != args.user:
                continue
            if args.role and frame.get('role') != args.role:
                continue
            if args.detect_gaps:
                seq = frame.get('seq')
                if isinstance(seq, int):
                    if last_seq is not None and seq != last_seq + 1:
                        gaps.append((path.name, last_seq, seq))
                    last_seq = seq
            sid = frame.get('session_id')
            if sid:
                sessions[sid] = sessions.get(sid, 0) + 1
            if args.msgpack:
                payload = msgpack.packb(frame, use_bin_type=True)
                sys.stdout.buffer.write(struct.pack('>I', len(payload)))
                sys.stdout.buffer.write(payload)
            else:
                if args.pretty:
                    print(json.dumps(frame, ensure_ascii=False, indent=2))
                else:
                    print(json.dumps(frame, ensure_ascii=False))
        
    if args.stats:
        print(f"[stats] frames={total} sessions={len(sessions)}", file=sys.stderr)
        for sid, cnt in sessions.items():
            print(f"[stats] session {sid} frames={cnt}", file=sys.stderr)
        if args.detect_gaps and gaps:
            for name, a, b in gaps:
                print(f"[gap] {name}: {a}->{b}", file=sys.stderr)

if __name__ == '__main__':
    main()
