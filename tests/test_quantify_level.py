from __future__ import annotations

from raiseup.domain.models import Achievement, Level
from raiseup.domain.rules.level import check, scope_counts
from raiseup.domain.rules.quantify import check as q_check
from raiseup.domain.rules.quantify import counted, is_quantified


def test_number_with_unit_counts():
    assert is_quantified("把时长降了 22%")


def test_number_without_unit_not_counts():
    assert not is_quantified("处理了 12 张表")


def test_no_number_not_counts():
    assert not is_quantified("整理了一份交接文档")


def test_check_flags_plain_text():
    findings = q_check([Achievement(1, "负责的项目按时上线")])
    assert findings[0].rule_id == "ach.no_number"


def test_counted_only_quantified():
    items = [Achievement(1, "降 22%"), Achievement(2, "整理文档")]
    assert counted(items) == 1


def test_scope_counts():
    items = [Achievement(1, "a", scope="team"), Achievement(2, "b", scope="org")]
    assert scope_counts(items) == {"team": 1, "org": 1}


def test_level_needs_count():
    items = [Achievement(1, "降 22%"), Achievement(2, "带 2 个新人")]
    findings = check(items, Level(1, "P6", 3, 4, ("team",)))
    assert any("只有 2 条" in f.message for f in findings)


def test_level_needs_scope():
    items = [Achievement(1, "降 22%", scope="team")]
    findings = check(items, Level(1, "P6", 3, 1, ("org",)))
    assert any("org" in f.target for f in findings)
