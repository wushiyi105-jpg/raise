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


def parse_json(text: str) -> dict:
    """模型常把 JSON 包在 ```json 里；取出第一个完整对象再解析。"""
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no json object")
    return json.loads(text[start : end + 1])


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
        data = parse_json(llm.write(PROMPT, "\n".join(facts)))
    except Exception:  # noqa: BLE001
        return "", []
    text = str(data.get("text", ""))
    return text, [f.message for f in check(text, items)]


def script(store: StorePort, text: str, expected: str = "0") -> list[str]:
    return [f.message for f in check(text, store.list_achievements(), [expected])]
