"""谈薪稿守卫：数字要能在证据里找到，"唯一/第一"这类话不许写。"""

from __future__ import annotations

import re

from .models import Achievement, Finding

PENALTY_NUMBER = 8
PENALTY_CLAIM = 6
NUM = re.compile(r"(\d+(?:\.\d+)?)")
CLAIMS = ("唯一", "第一", "无人能替", "不可替代", "史上")


def _norm(s: str) -> str:
    return s.rstrip("0").rstrip(".") if "." in s else s


def evidence_numbers(items: list[Achievement]) -> set[str]:
    out: set[str] = set()
    for a in items:
        for m in NUM.findall(a.text):
            out.add(m)
            out.add(_norm(m))
    return out


def check(text: str, items: list[Achievement], extra: list[str] | None = None) -> list[Finding]:
    out: list[Finding] = []
    ok = evidence_numbers(items)
    for e in extra or []:
        ok.add(e)
    bad = [n for n in NUM.findall(text) if n not in ok and _norm(n) not in ok]
    if bad:
        out.append(
            Finding("guard.number", f"稿里提到 {'、'.join(sorted(set(bad)))}，证据里没有，删掉", PENALTY_NUMBER, "script")
        )
    claim = next((c for c in CLAIMS if c in text), None)
    if claim:
        out.append(
            Finding("guard.claim", f"写了「{claim}」，评审只认证据，改成具体数字", PENALTY_CLAIM, claim)
        )
    return out
