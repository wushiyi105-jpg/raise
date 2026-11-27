"""用例：量化率 → 职级差距 → 模型起草 → 数字与措辞守卫。"""

from __future__ import annotations

import json
from pathlib import Path

from ..config import Settings
from ..domain.engine import build, top
from ..domain.guard import check
from ..domain.models import Readiness
from ..ports import LLMPort, StorePort

PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "material.md").read_text(encoding="utf-8")


def readiness(store: StorePort, level: str | None = None) -> Readiness:
    return build(store.list_achievements(), store.level(level), store.list_reviews())


def draft(
    store: StorePort,
    settings: Settings,
    level: str | None = None,
    llm: LLMPort | None = None,
) -> tuple[str, list[str]]:
    items = store.list_achievements()
    if llm is None:
        return "", []
    facts = [a.text for a in top(items, 6)]
    try:
        data = json.loads(llm.write(PROMPT, "\n".join(facts)))
    except Exception:  # noqa: BLE001
        return "", []
    text = str(data.get("text", ""))
    return text, [f.message for f in check(text, items)]


def script(store: StorePort, text: str, expected: str = "0") -> list[str]:
    return [f.message for f in check(text, store.list_achievements(), [expected])]
