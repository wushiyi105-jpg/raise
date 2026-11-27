"""本地模板：P5–P7 能力项、谈薪五阶段。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parents[2] / "data"


@lru_cache(maxsize=1)
def templates() -> dict[str, Any]:
    return json.loads((DATA / "level_templates.json").read_text(encoding="utf-8"))


def levels() -> list[dict[str, Any]]:
    return list(templates()["levels"])


def level(code: str) -> dict[str, Any]:
    for x in levels():
        if x["code"] == code:
            return x
    names = "、".join(x["code"] for x in levels())
    raise ValueError(f"没有 {code} 的模板，可选：{names}")


def stages() -> list[dict[str, Any]]:
    return list(templates()["stages"])


def opening() -> list[str]:
    return list(templates()["opening"])
