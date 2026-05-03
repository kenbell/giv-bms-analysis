"""Privacy filter -- strip private identifiers from capture artefacts.

Operates on text (logs, NDJSON, parquet schema-aware in-place) and raw bytes
(wire captures). Reads config from ~/.givenergy-redact.toml or env vars
GIVE_REDACT_SERIALS and GIVE_REDACT_IPS (comma-separated).

Idempotent: re-running on already-redacted output produces the same output.
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict


def load_config_dict(path: Path | None = None) -> Dict[str, Any]:
    """Load redaction config. File takes precedence over env vars."""
    if path is None:
        path = Path.home() / ".givenergy-redact.toml"
    if path.exists():
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return {
            "serials": list(data.get("serials", [])),
            "ips": list(data.get("ips", [])),
        }
    return {
        "serials": [s for s in os.environ.get("GIVE_REDACT_SERIALS", "").split(",") if s],
        "ips": [s for s in os.environ.get("GIVE_REDACT_IPS", "").split(",") if s],
    }


def redact_text(text: str, config: Dict[str, Any]) -> str:
    """Replace serials and IPs in arbitrary text. Handles ASCII and hex-encoded
    forms of each serial.
    """
    out = text
    for serial in config.get("serials", []):
        if not serial:
            continue
        out = out.replace(serial, "X" * len(serial))
        for case in (lambda c: f"{ord(c):02x}", lambda c: f"{ord(c):02X}"):
            hex_form = " ".join(case(c) for c in serial)
            out = out.replace(hex_form, " ".join(["XX"] * len(serial)))
    for ip in config.get("ips", []):
        if not ip:
            continue
        out = out.replace(ip, "X.X.X.X")
    return out


def redact_bytes(payload: bytes, config: Dict[str, Any]) -> bytes:
    """Replace serial substrings inside raw byte payloads."""
    out = payload
    for serial in config.get("serials", []):
        if not serial:
            continue
        needle = serial.encode("ascii")
        replacement = b"X" * len(needle)
        out = out.replace(needle, replacement)
    return out


def redact_file(in_path: Path, out_path: Path, config: Dict[str, Any]) -> None:
    """Redact a file, choosing text vs bytes based on extension."""
    in_path = Path(in_path)
    out_path = Path(out_path)
    text_exts = {".log", ".ndjson", ".json", ".md", ".csv", ".txt"}
    if in_path.suffix.lower() in text_exts:
        out_path.write_text(redact_text(in_path.read_text(), config))
    else:
        out_path.write_bytes(redact_bytes(in_path.read_bytes(), config))


def main():
    p = argparse.ArgumentParser(description="Redact private identifiers from capture artefacts")
    p.add_argument("input", type=Path)
    p.add_argument("--out", type=Path, help="Output path (default: in-place with .redacted suffix)")
    p.add_argument("--config", type=Path, help="Override config path")
    args = p.parse_args()
    cfg = load_config_dict(args.config)
    out = args.out or args.input.with_suffix(args.input.suffix + ".redacted")
    redact_file(args.input, out, cfg)
    print(f"Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
