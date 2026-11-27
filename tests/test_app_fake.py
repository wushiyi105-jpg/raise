"""主用例只依赖 ports：用 MagicMock 内存假实现，不建 SQLite 文件。"""

from __future__ import annotations

from unittest.mock import MagicMock

from raiseup.app.run import readiness
from raiseup.ports import StorePort


def test_main_path_with_memory_store(tmp_path) -> None:
    store = MagicMock(spec=StorePort)
    store.level.return_value = None
    store.list_achievements.return_value = []
    store.list_reviews.return_value = []
    
    out = readiness(store)
    assert out is not None
    assert not (tmp_path / "app.db").exists()
