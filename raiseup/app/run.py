"""用例：量化率 → 职级差距 → 模型起草 → 数字与措辞守卫。"""

from __future__ import annotations

import json

from ..adapters.llm import build_llm
from ..adapters.store import SqliteStore
from ..config import Settings
from ..domain.engine import build, top
from ..domain.guard import check
from ..domain.models import Readiness

PROMPT = """把给出成果改写成晋升材料里的三段话，只能用输入里已有的数字。
不许写"唯一""第一""不可替代"。输出 JSON：{"text": "…"}"""


def readiness(store: SqliteStore, level: str | None = None) -> Readiness:
    return build(store.list_achievements(), store.level(level), store.list_reviews())


def draft(store: SqliteStore, settings: Settings, level: str | None = None) -> tuple[str, list[str]]:
    items = store.list_achievements()
    if not settings.llm_enabled:
        return "", []
    facts = [a.text for a in top(items, 6)]
    llm = build_llm(settings.llm_base_url, settings.llm_api_key, settings.llm_model, PROMPT)
    try:
        data = json.loads(llm.write(PROMPT, "\n".join(facts)))
    except Exception:  # noqa: BLE001
        return "", []
    text = str(data.get("text", ""))
    return text, [f.message for f in check(text, items)]


def script(store: SqliteStore, text: str, expected: str = "0") -> list[str]:
    return [f.message for f in check(text, store.list_achievements(), [expected])]
