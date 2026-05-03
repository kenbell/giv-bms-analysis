"""Tests for the tag annotation helper."""
import json
from pathlib import Path

from tools.tag import write_tag, detect_changes


def test_write_tag_appends_record(tmp_path):
    out = tmp_path / "tags.ndjson"
    write_tag(out, "force_charge_start")
    lines = out.read_text().strip().split("\n")
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["tag"] == "force_charge_start"
    assert rec["source"] == "manual"
    assert "ts" in rec


def test_write_tag_two_records_appended(tmp_path):
    out = tmp_path / "tags.ndjson"
    write_tag(out, "a")
    write_tag(out, "b", source="auto")
    lines = out.read_text().strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[1])["source"] == "auto"


def test_detect_changes_yields_transition_pairs():
    records = [
        {"fields": {"mode": "idle"}},
        {"fields": {"mode": "idle"}},
        {"fields": {"mode": "charge"}},
        {"fields": {"mode": "charge"}},
        {"fields": {"mode": "idle"}},
    ]
    changes = list(detect_changes(records, "mode"))
    assert changes == [("idle", "charge"), ("charge", "idle")]


def test_detect_changes_skips_missing_field():
    records = [
        {"fields": {"mode": "idle"}},
        {"fields": {}},
        {"fields": {"mode": "idle"}},
        {"fields": {"mode": "charge"}},
    ]
    changes = list(detect_changes(records, "mode"))
    assert changes == [("idle", "charge")]
