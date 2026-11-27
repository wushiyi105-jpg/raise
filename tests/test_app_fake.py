"""真实内存 Store 跑 readiness：不建 SQLite，mypy 校验 StorePort。"""

from __future__ import annotations

from raiseup.app.run import readiness
from raiseup.domain.models import Achievement, Level, Review
from raiseup.ports import StorePort


class InMemoryStore:
    def list_achievements(self) -> list[Achievement]:
        return []

    def level(self, code: str | None = None) -> Level | None:
        return None

    def list_reviews(self) -> list[Review]:
        return []


def test_readiness_with_memory_store() -> None:
    store: StorePort = InMemoryStore()
    out = readiness(store)
    assert out.total == 0
