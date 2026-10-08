# 示例：AI 陪伴硬件 Mapping（虚构）

一个端到端的虚构示例：同一个任务、同一组来源，一份合格的产出和一份故意犯错的产出。所有公司、机构、媒体与数字均为虚构。

| 文件 | 内容 |
|---|---|
| `task.md` | 任务原文与决策时点（`asof` = 2026-09-30） |
| `sources.json` | 13 个来源，每个带发布日期、origin、实体与事件 |
| `report.md` | 正式产出：Summary → 分类口径 → 总表 → 机构画像 → 项目画像 → 来源附录，外加给 reviewer 的汇报 |
| `run.json` | 与报告对应的 run record，8 个关口全部通过 |
| `run_bad.json` | 同一任务的错误示范，8 个关口全部失败 |
| `landscape.csv` · `landscape.config.json` | 市场格局图的底表与配置 |

## 来源里埋了什么

| 来源 | 设计目的 |
|---|---|
| S-01 + S-12 | 同一笔融资，媒体报道与公司官方账号各一份：两类公开来源相互印证，可以标「核实」 |
| S-02 | 公司 BP：无论 run record 怎么声明，最多「待DD」 |
| S-05 | 群聊截图里的融资传闻：只来自非公开渠道的早期项目，必须带状态入池，不能被漏掉 |
| S-07 | 创始人访谈：融资与客户都是公司口径，「待DD」 |
| S-09 | 发布于 2026-10-15，晚于决策时点：不写进工作区，引用即判为后视泄露 |
| S-11 | 没有发布日期：允许使用，但在清单里标为 undated |
| S-13 | 有融资事件，但项目不在研究边界内：必须在 `excluded_from_pool` 写明排除理由 |

## 跑一遍

```bash
E=examples/ai-companion-hardware
irh assemble "帮我做 AI 陪伴硬件赛道的 mapping，看哪些机构投了" --asof 2026-09-30 --sources $E/sources.json
irh check $E/run.json     --sources $E/sources.json
irh check $E/run_bad.json --sources $E/sources.json
irh score $E/run.json     --sources $E/sources.json --judge "Judgment quality=2"
```

画格局图（需要 `pip install -e ".[viz]"`）：

```bash
python skills/landscape-visualization/scripts/render_market_landscape_html.py \
  --input $E/landscape.csv --config $E/landscape.config.json \
  --output landscape.html --title "AI 陪伴硬件市场格局（虚构示例）"
```

同一任务的杂乱版本，作为评测用例放在 `agent/evals/cases/mapping_intent_messy_input.md`。
