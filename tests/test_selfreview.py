"""晋升自评稿：STAR 四段齐全、五阶段、未知级别报错。"""

from __future__ import annotations

import pytest

from raiseup.app.selfreview import build_review


def test_review_has_star_and_stages() -> None:
    text = build_review("P6")
    assert "## 二、可直接粘贴的 STAR 自评稿" in text
    assert "**S 情境**" in text and "**R 结果**" in text
    assert text.count("**S 情境**") >= 5
    assert "## 四、谈薪开场三句（直接念）" in text
    assert text.count("### ") >= 10
    assert "谈薪五阶段" in text


def test_review_p5_uses_three_records() -> None:
    text = build_review("P5")
    assert "# 晋升自评 · P5" in text
    assert text.count("**S 情境**") == 3


def test_review_unknown_level() -> None:
    with pytest.raises(ValueError, match="没有 P9"):
        build_review("P9")
