"""量化识别：成果里至少要有一个带单位的数字。"""

from __future__ import annotations

import re

from ..models import Achievement, Finding

PENALTY = 5
UNITS = ("%", "万", "元", "人", "天", "小时", "次", "个", "条", "倍", "台", "篇", "家")
NUM = re.compile(r"\d+(?:\.\d+)?")


def is_quantified(text: str) -> bool:
    return bool(NUM.search(text)) and any(u in text for u in UNITS)


def check(items: list[Achievement]) -> list[Finding]:
    out: list[Finding] = []
    for a in items:
        if not is_quantified(a.text):
            out.append(
                Finding("ach.no_number", f"「{a.text[:24]}」没有数字或单位，写不成证据", PENALTY, str(a.id))
            )
    return out


def counted(items: list[Achievement]) -> int:
    return sum(1 for a in items if is_quantified(a.text))
