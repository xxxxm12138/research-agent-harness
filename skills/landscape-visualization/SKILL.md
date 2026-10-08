---
name: landscape-visualization
description: 把赛道 mapping / 机构画像底表画成研报风格的多面板市场格局图（PNG / SVG）或可交互 HTML。适用于"市场格局可视化""机构-项目统计图""画成研报图""参考多图拼版风格"等任务。
---

# 市场格局可视化

## 目标

把项目、机构、融资、类别等底表转成一张可放进报告的多面板 infographic。风格参考学术 poster / 研报图：浅底、低饱和蓝绿黄、细网格、多图块、少装饰、信息密度高。

图是分析界面，不是装饰：先写结论和口径，再放图（见 `agent/checkpoint_workflow.md` 的 Visualization Gate）。

## 输入

优先使用 CSV。至少包含：

| 字段 | 含义 |
|---|---|
| project | 项目名 |
| category | 一级分类（与 Mapping 主轴一致） |
| sub_type | 产品形态 / 子类 |
| region | 国内 / 海外 / 大厂参照 / 用户线索 |
| stage | 融资轮次 |
| amount_usd_m | 美元百万口径金额；只填公开披露或可换算的金额，未知留空 |
| amount_label | 原始金额描述（含信息状态，如"传闻近千万美元（市场线索待核验）"） |
| investors | 投资方，用 `;` 分隔 |
| lead_investors | 领投方，用 `;` 分隔 |
| investor_types | 机构属性，用 `;` 分隔 |
| source_status | 信息状态：核实 / 公开报道 / 媒体口径 / 市场线索待核验 / 待DD / 未公开 |

## 配置（口径写在数据旁边）

机构关注名单、排除名单、标签缩写、二维地图坐标都放在 JSON 配置里，不写进脚本。从 `skills/landscape-visualization/config.example.json` 复制一份放在数据旁边：

| 键 | 作用 |
|---|---|
| `ignore_investors` | 不计入机构统计的占位值（如"待 DD"） |
| `canonical_investors` | 同一机构不同写法的归一 |
| `heatmap_focus_investors` | 热力图在"参与数前 10"之外必须展示的机构（reviewer 关心但排名靠后的） |
| `heatmap_exclude_investors` | 不进热力图的投资方（如个人天使），并在图注说明 |
| `short_labels` | 长名称的图上缩写 |
| `type_labels` | 资金属性归一 |
| `market_map.x_by_category` / `y_by_sub_type` | 二维地图坐标：横轴通常是 Mapping 主轴，纵轴是第二维度 |
| `market_map.x_ticks` / `y_ticks` | 坐标轴刻度与含义 |

一个完整的虚构示例：`examples/ai-companion-hardware/landscape.csv` + `examples/ai-companion-hardware/landscape.config.json`。

## 图面结构

一张横向大图，8 个面板加样本速览：

1. **样本口径**：项目数、机构数、类别数、有公开金额的项目数。
2. **A 类别项目数 / 融资额**：横向柱状图。
3. **B 项目融资散点**：项目按金额、类别展开。
4. **C 机构-类别热力图**：机构投过哪些类别（入选规则写在图注）。
5. **D 机构投资次数**：按项目数排序。
6. **E 轮次分布**：各类别处于哪些融资阶段。
7. **F 资金属性分布**：财务 VC / 产业资本 / 政府基金等。
8. **G 二维市场地图**：横轴、纵轴含义来自配置。
9. **H 样本项目速览**：项目、分类、轮次、金额、信息状态。

## 口径要求

- 不把未知金额硬转成 0；金额未知的项目只参与项目数统计。
- 待DD、传闻与用户线索不计入金额合计。
- 大厂内部产品可标为参照，不计入独立融资统计，除非 reviewer 要求纳入。
- 投资偏好只写"可观察到 / 可能说明 / 待DD"，不写成最终投资建议。
- 图注说明：公开信息不足处为待DD；热力图的入选规则。

## 绘图

需要可视化依赖：`pip install -e ".[viz]"`。

```bash
python skills/landscape-visualization/scripts/render_market_landscape.py \
  --input examples/ai-companion-hardware/landscape.csv \
  --config examples/ai-companion-hardware/landscape.config.json \
  --output landscape.png --title "AI 陪伴硬件市场格局（虚构示例）"
```

加 `--format svg` 输出矢量图。

## 交互 HTML

```bash
python skills/landscape-visualization/scripts/render_market_landscape_html.py \
  --input examples/ai-companion-hardware/landscape.csv \
  --config examples/ai-companion-hardware/landscape.config.json \
  --output landscape.html --title "AI 陪伴硬件市场格局（虚构示例）"
```

交互版包含：分类 / 地域 / 资金属性筛选、项目与机构搜索、KPI 自动刷新、各面板 hover 提示、可点击的项目表与详情面板（含信息状态）。页面是单个静态文件，数据嵌在页面里；CSV 中的文本在写入页面前都会转义。更新 CSV 后重新运行即可。

## 输出检查

- 中文不乱码（脚本会自动选择系统里可用的中文字体）。
- 每个面板标题清楚，坐标轴含义写明。
- 图里不出现未经核验的确定性结论。
- 金额未知较多时，在图下注明"金额统计仅包含公开披露金额的项目"。
- 计数与报告正文、run record 的 `summary` 一致（同一张最终底表）。
