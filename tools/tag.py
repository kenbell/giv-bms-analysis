"""Scenario annotation helper.

Manual mode: `python tools/tag.py <name> --out tags.ndjson` appends one record.
Auto mode:   `python tools/tag.py --auto --tcp tcp.ndjson --field inverter_status --out tags.ndjson`
             tails tcp.ndjson and emits a tag whenever `field` value changes.
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator


def write_tag(out_path: Path, tag: str, source: str = "manual") -> dict:
    """Append one timestamped tag record to `out_path` (NDJSON)."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tag": tag,
        "source": source,
    }
    out_path = Path(out_path)
    with open(out_path, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record


def detect_changes(records: Iterable[dict], field: str) -> Iterator[tuple]:
    """Yield (prev_value, new_value) pairs whenever `field` changes between
    consecutive records that contain it. Records missing the field are skipped
    rather than treated as transitions.
    """
    last = None
    for rec in records:
        value = rec.get("fields", {}).get(field)
        if value is None:
            continue
        if last is not None and value != last:
            yield (last, value)
        last = value


def _tail_records(path: Path):
    """Yield decoded NDJSON records as new lines arrive."""
    with open(path) as f:
        f.seek(0, 2)  # EOF
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _run_auto(tcp_path: Path, out_path: Path, field: str):
    last = None
    for rec in _tail_records(tcp_path):
        value = rec.get("fields", {}).get(field)
        if value is None:
            continue
        if last is not None and value != last:
            write_tag(out_path, f"auto:{field}:{last}->{value}", source="auto")
        last = value


def main():
    p = argparse.ArgumentParser(description="Tag scenario transitions during a capture")
    p.add_argument("tag", nargs="?", help="Tag name (manual mode)")
    p.add_argument("--out", type=Path, default=Path("tags.ndjson"))
    p.add_argument("--auto", action="store_true", help="Auto-detect transitions from TCP stream")
    p.add_argument("--tcp", type=Path, help="Path to tcp.ndjson (required with --auto)")
    p.add_argument("--field", default="inverter_status",
                   help="TCP field to watch for state changes (default: inverter_status)")
    args = p.parse_args()

    if args.auto:
        if args.tcp is None:
            print("--auto requires --tcp", file=sys.stderr)
            sys.exit(2)
        _run_auto(args.tcp, args.out, args.field)
    else:
        if not args.tag:
            print("manual mode requires a tag argument", file=sys.stderr)
            sys.exit(2)
        rec = write_tag(args.out, args.tag, "manual")
        print(json.dumps(rec))


if __name__ == "__main__":
    main()
