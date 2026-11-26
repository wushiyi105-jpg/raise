"""复盘稿：S/T/A/R 四段都要有，缺哪段说哪段。"""

from __future__ import annotations

from ..models import STAR, STAR_LABEL, Finding, Review

PENALTY = 4


def missing(review: Review) -> list[str]:
    return [s for s in STAR if s not in review.sections]


def check(reviews: list[Review]) -> list[Finding]:
    out: list[Finding] = []
    for r in reviews:
        for s in missing(r):
            out.append(
                Finding(
                    "review.star",
                    f"复盘 #{r.id} 缺 {s}（{STAR_LABEL[s]}）",
                    PENALTY,
                    f"{r.id}/{s}",
                )
            )
    return out
