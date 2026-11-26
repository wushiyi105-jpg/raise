from __future__ import annotations

from raiseup.domain.guard import check
from raiseup.domain.models import Achievement, Review
from raiseup.domain.rules.star import check as star_check
from raiseup.domain.rules.star import missing


def test_full_star_no_finding():
    assert star_check([Review(1, "故事", "P6", ("S", "T", "A", "R"))]) == []


def test_missing_two_sections():
    findings = star_check([Review(1, "故事", "P6", ("A", "R"))])
    assert [f.rule_id for f in findings] == ["review.star", "review.star"]


def test_missing_lists_order():
    assert missing(Review(1, "x", "", ("R",))) == ["S", "T", "A"]


def test_guard_flags_unknown_number():
    items = [Achievement(1, "降 22%")]
    findings = check("我让效率提升 37%", items)
    assert findings[0].rule_id == "guard.number"


def test_guard_accepts_known_number():
    items = [Achievement(1, "降 22%")]
    assert check("处理时长降 22%", items) == []


def test_guard_flags_claim_word():
    items = [Achievement(1, "降 22%")]
    findings = check("这块业务我是唯一负责人", items)
    assert findings[0].rule_id == "guard.claim"


def test_guard_extra_numbers_allowed():
    items = [Achievement(1, "降 22%")]
    assert check("期望调薪 15%", items, ["15"]) == []
