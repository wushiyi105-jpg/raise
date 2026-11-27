"""晋升自评：选级别 → 取记录里最强的几条 → STAR 稿 + 谈薪五阶段。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..domain.catalog import level as level_data
from ..domain.catalog import levels as all_levels
from ..domain.catalog import opening, stages

DATA = Path(__file__).resolve().parents[2] / "data" / "seed.json"


def _records() -> list[dict[str, Any]]:
    return list(json.loads(DATA.read_text(encoding="utf-8"))["achievements"])


def _has_number(text: str) -> bool:
    return bool(re.search(r"\d", text or ""))


def build_review(level_code: str) -> str:
    lv = level_data(level_code)
    records = _records()
    quantified = sum(1 for r in records if _has_number(r["text"]))
    scopes: dict[str, int] = {}
    for r in records:
        scopes[r["scope"]] = scopes.get(r["scope"], 0) + 1
    picked = sorted(records, key=lambda r: r["impact"], reverse=True)[: lv["need_count"]]

    lines = [
        f"# 晋升自评 · {level_code}",
        "",
        f"> 依据：{lv['evidence']}；能力项 {('、'.join(lv['competencies']))}。",
        f"> 记录里共 {len(records)} 条成果，其中 {quantified} 条带数字；范围分布 "
        + "、".join(f"{k} {v} 条" for k, v in sorted(scopes.items()))
        + "。",
        "",
        "## 一、结论",
        "",
    ]
    if quantified >= lv["need_count"]:
        lines.append(f"- 量化成果 {quantified} 条，达到 {level_code} 的 {lv['need_count']} 条门槛。")
    else:
        lines.append(f"- 量化成果 {quantified} 条，离 {level_code} 的 {lv['need_count']} 条还差 {lv['need_count'] - quantified} 条。")
    for need in lv["need_scope"]:
        n = scopes.get(need, 0)
        lines.append(f"- {need} 范围 {n} 条（门槛 2 条）。" if n < 2 else f"- {need} 范围 {n} 条，够。")

    lines += ["", "## 二、可直接粘贴的 STAR 自评稿", ""]
    for i, r in enumerate(picked, 1):
        lines += [
            f"### {i}. {r['text']}（{r['quarter']}｜影响 {r['impact']}/10）",
            "",
            f"**S 情境**：{r.get('s') or r['text']}",
            "",
            f"**T 任务**：{r.get('t') or '把这件事推进到可复用结果'}",
            "",
            f"**A 动作**：{r.get('a') or r['text']}",
            "",
            f"**R 结果**：{r.get('r') or r['text']}",
            "",
        ]

    lines += [
        "## 三、能力项对照（P5–P7）",
        "",
        "| 级别 | 年限 | 证据要求 | 能力项 |",
        "| --- | --- | --- | --- |",
    ]
    for x in all_levels():
        lines.append(
            f"| {x['code']} | {x['years']} 年 | {x['evidence']} | {'、'.join(x['competencies'])} |"
        )

    lines += [
        "",
        "## 四、谈薪开场三句（直接念）",
        "",
        "```text",
        *opening(),
        "```",
        "",
        "## 五、谈薪五阶段",
        "",
    ]
    for s in stages():
        lines += [
            f"### {s['name']}",
            "",
            f"目标：{s['goal']}",
            "",
            "- 可以这样说：",
            *[f"  - “{x}”" for x in s["say"]],
            f"- 不要说：{s['avoid']}",
            "",
        ]

    lines += [
        "---",
        "",
        "数字出处：每条 R 里的数字都来自 `data/seed.json` 的 `achievements` 记录；"
        "本稿由本地模板拼接，未调用模型，不新增任何记录外的数字。",
        "",
    ]
    return "\n".join(lines)
