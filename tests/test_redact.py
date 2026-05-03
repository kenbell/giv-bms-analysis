"""Tests for redact.py -- verify ASCII serial, hex-encoded serial, and IP redaction."""
import pytest

from tools.redact import redact_text, redact_bytes, load_config_dict


def test_redact_text_replaces_ascii_serial():
    cfg = {"serials": ["DX2319G279"]}
    out = redact_text("inverter DX2319G279 reports OK", cfg)
    assert "DX2319G279" not in out
    assert "X" * 10 in out


def test_redact_text_replaces_ip():
    cfg = {"ips": ["192.168.1.42"]}
    out = redact_text("connecting to 192.168.1.42:8899", cfg)
    assert "192.168.1.42" not in out
    assert "X.X.X.X" in out


def test_redact_text_idempotent():
    cfg = {"serials": ["ABC"]}
    once = redact_text("hi ABC bye", cfg)
    twice = redact_text(once, cfg)
    assert once == twice


def test_redact_bytes_replaces_serial_in_byte_payload():
    payload = b"\x01\x02ABC\x03\x04"
    cfg = {"serials": ["ABC"]}
    out = redact_bytes(payload, cfg)
    assert b"ABC" not in out
    assert out == b"\x01\x02XXX\x03\x04"


def test_redact_text_handles_empty_config():
    cfg = {}
    text = "nothing to redact"
    assert redact_text(text, cfg) == text


def test_load_config_dict_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("GIVE_REDACT_SERIALS", "AAA,BBB")
    monkeypatch.setenv("GIVE_REDACT_IPS", "10.0.0.1")
    # Pass nonexistent path so file lookup falls through to env
    cfg = load_config_dict(tmp_path / "nonexistent.toml")
    assert "AAA" in cfg["serials"]
    assert "BBB" in cfg["serials"]
    assert "10.0.0.1" in cfg["ips"]
