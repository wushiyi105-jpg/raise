"""职级对齐：P 级要几条证据、要不要跨团队。"""

from __future__ import annotations

from ..models import Achievement, Finding, Level
from .quantify import counted

PENALTY = 6


def scope_counts(items: list[Achievement]) -> dict[str, int]:
    out: dict[str, int] = {}
    for a in items:
        out[a.scope] = out.get(a.scope, 0) + 1
    return out


def check(items: list[Achievement], level: Level) -> list[Finding]:
    out: list[Finding] = []
    n = counted(items)
    if n < level.need_count:
        out.append(
            Finding(
                "level.gap",
                f"{level.code} 要 {level.need_count} 条量化成果，现在只有 {n} 条",
                PENALTY,
                level.code,
            )
        )
    scopes = scope_counts(items)
    for need in level.need_scope:
        if scopes.get(need, 0) < 2:
            out.append(
                Finding(
                    "level.gap",
                    f"{level.code} 要至少 2 条 {need} 范围的成果，现在 {scopes.get(need, 0)} 条",
                    PENALTY,
                    f"{level.code}/{need}",
                )
            )
    return out
