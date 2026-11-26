from __future__ import annotations

from fastapi.testclient import TestClient

from raiseup.adapters.store import SqliteStore
from raiseup.domain.engine import build, top
from raiseup.domain.models import Achievement
from raiseup.iface.web import create_app


def _seed(store: SqliteStore):
    store.add_achievement("降 22%", 7, "team", "2026Q3")
    store.add_achievement("整理文档", 2, "team", "2026Q3")
    store.add_level("P6", 3, 5, ["team"])
    store.add_review("故事", "P6", ["A", "R"])


def test_readiness_ratio():
    r = build([Achievement(1, "降 22%"), Achievement(2, "文档")], None, [])
    assert r.ratio == 0.5
    assert r.total == 2


def test_readiness_without_level_skips_level_rule():
    r = build([Achievement(1, "文档")], None, [])
    assert all(f.rule_id != "level.gap" for f in r.findings)


def test_top_by_impact():
    items = [Achievement(1, "a", 3), Achievement(2, "b", 9), Achievement(3, "c", 5)]
    assert [a.id for a in top(items, 2)] == [2, 3]


def test_index_page(store, settings):
    _seed(store)
    client = TestClient(create_app(settings, store))
    body = client.get("/").text
    assert client.get("/").status_code == 200
    assert "成果台账" in body


def test_index_with_level_filter(store, settings):
    _seed(store)
    r = TestClient(create_app(settings, store)).get("/?level=P6")
    assert r.status_code == 200
