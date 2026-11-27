# 更新记录

## Unreleased

- 种子扩到 12 条成果，每条带 S/T/A/R 事实；新增 P5–P7 能力项模板与谈薪五阶段
- 新增 `selfreview` 命令：一次出可粘贴 STAR 自评稿、能力项对照、开场三句与五阶段话术
- `0001_init` 改为显式 `op.create_table` / `op.create_index`，运行期走 `alembic upgrade`
- `app/` 只依赖 `ports`，新增内存假实现用例
- 开 ruff `E2`/`E3`；CI 增加 `docker build` 与 `/health` 探活

## 1.0.0

- 量化识别（数字 + 单位）
- P 级条数与范围对齐
- STAR 四段校验
- 谈薪稿数字与措辞守卫
