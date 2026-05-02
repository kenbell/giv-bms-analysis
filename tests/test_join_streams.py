"""Tests for join_streams - verify forward-fill of TCP into wire frames and
tag association via merge_asof.
"""
import pandas as pd
import pytest

from tools.join_streams import join_streams


def _ts(s):
    return pd.Timestamp(s)


def test_join_streams_forward_fills_tcp_into_wire_rows():
    wire = pd.DataFrame([
        {"ts": _ts("2026-05-02T10:00:01"), "fc": 4, "fld_x": 1},
        {"ts": _ts("2026-05-02T10:00:02"), "fc": 4, "fld_x": 2},
        {"ts": _ts("2026-05-02T10:00:03"), "fc": 4, "fld_x": 3},
    ])
    tcp = pd.DataFrame([
        {"ts": _ts("2026-05-02T10:00:00"), "tcp_soc": 50},
        {"ts": _ts("2026-05-02T10:00:02"), "tcp_soc": 51},
    ])
    tags = pd.DataFrame()
    joined = join_streams(wire, tcp, tags)
    assert list(joined["tcp_soc"]) == [50, 51, 51]


def test_join_streams_attaches_active_tag():
    wire = pd.DataFrame([
        {"ts": _ts("2026-05-02T10:00:01"), "fc": 4, "fld_x": 1},
        {"ts": _ts("2026-05-02T10:00:05"), "fc": 4, "fld_x": 2},
    ])
    tcp = pd.DataFrame([{"ts": _ts("2026-05-02T10:00:00"), "tcp_soc": 50}])
    tags = pd.DataFrame([
        {"ts": _ts("2026-05-02T10:00:00"), "tag": "idle", "source": "manual"},
        {"ts": _ts("2026-05-02T10:00:04"), "tag": "force_charge_start", "source": "manual"},
    ])
    joined = join_streams(wire, tcp, tags)
    assert joined.iloc[0]["active_tag"] == "idle"
    assert joined.iloc[1]["active_tag"] == "force_charge_start"


def test_join_streams_handles_empty_tags():
    wire = pd.DataFrame([{"ts": _ts("2026-05-02T10:00:01"), "fld_x": 1}])
    tcp = pd.DataFrame([{"ts": _ts("2026-05-02T10:00:00"), "tcp_soc": 50}])
    tags = pd.DataFrame()
    joined = join_streams(wire, tcp, tags)
    assert "active_tag" in joined.columns
    assert pd.isna(joined.iloc[0]["active_tag"])


def test_join_streams_handles_empty_tcp():
    wire = pd.DataFrame([{"ts": _ts("2026-05-02T10:00:01"), "fld_x": 1}])
    tcp = pd.DataFrame()
    tags = pd.DataFrame()
    joined = join_streams(wire, tcp, tags)
    assert len(joined) == 1
    assert joined.iloc[0]["fld_x"] == 1
