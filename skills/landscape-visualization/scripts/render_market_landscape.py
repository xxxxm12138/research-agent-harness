#!/usr/bin/env python3
"""Render a mapping bottom table as a multi-panel, report-style market landscape.

Usage:
    python render_market_landscape.py --input data.csv --output out.png \
        --title "示例赛道市场格局" [--config landscape.config.json] [--format svg]

Requires pandas, numpy and matplotlib (``pip install -e ".[viz]"``). Investor focus
lists, label overrides and market-map coordinates come from ``--config``.
"""

from __future__ import annotations

import argparse
import zlib
from collections import Counter
from textwrap import shorten, wrap

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _landscape_config import (
    LandscapeConfig,
    category_x,
    heatmap_investors,
    investor_items,
    load_config,
    type_items,
    unique_in_order,
)

PALETTE = {
    "blue": "#7FA6C7",
    "teal": "#7AB7B0",
    "green": "#9CC7A5",
    "yellow": "#F1CF85",
    "orange": "#E6A56F",
    "purple": "#B7A6D8",
    "gray": "#AEB7C2",
    "ink": "#2F3A42",
    "muted": "#66727D",
    "grid": "#DCE5E4",
    "paper": "#F8FAF7",
    "panel": "#FFFFFF",
}
SERIES = ["blue", "green", "yellow", "purple", "orange", "teal", "gray"]
REGION_COLORS = {"国内": "green", "海外": "blue", "大厂参照": "yellow", "用户线索": "gray"}
STAGE_ORDER = ["Pre-seed", "种子", "Seed", "天使", "Angel", "Pre-A", "A", "A+", "B", "B+", "C"]
TEXT_COLUMNS = (
    "project",
    "category",
    "sub_type",
    "region",
    "stage",
    "amount_label",
    "investors",
    "lead_investors",
    "investor_types",
    "source_status",
)
FONT_CANDIDATES = (
    "PingFang SC",
    "Hiragino Sans GB",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Microsoft YaHei",
    "SimHei",
    "Arial Unicode MS",
)


def pick_font() -> str:
    installed = {f.name for f in fm.fontManager.ttflist}
    return next((name for name in FONT_CANDIDATES if name in installed), "DejaVu Sans")


def color(index: int) -> str:
    return PALETTE[SERIES[index % len(SERIES)]]


def short(value: object, cfg: LandscapeConfig, width: int = 18) -> str:
    text = str(value)
    return cfg.short_labels.get(text, shorten(text, width=width, placeholder="..."))


def jitter(key: str, scale: float) -> float:
    """Deterministic offset in [-scale, scale] so reruns draw the same picture."""
    return (zlib.crc32(key.encode("utf-8")) % 2001 / 1000 - 1) * scale


def normalize_stage(value: object) -> str:
    text = str(value).replace("轮", "").strip()
    if not text or text.lower() == "nan":
        return "待 DD"
    for stage in STAGE_ORDER:
        if text.lower() == stage.lower():
            return stage
    return text


def amounts(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df["amount_usd_m"], errors="coerce")


def setup_ax(ax, title: str) -> None:
    ax.set_facecolor(PALETTE["panel"])
    for spine in ax.spines.values():
        spine.set_color("#D7DEDC")
        spine.set_linewidth(0.8)
    ax.grid(True, color=PALETTE["grid"], linewidth=0.7, alpha=0.75)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=PALETTE["ink"], pad=10)
    ax.tick_params(colors=PALETTE["muted"], labelsize=9)
    ax.set_axisbelow(True)


def draw_summary(ax, df: pd.DataFrame, title: str, cfg: LandscapeConfig) -> None:
    ax.axis("off")
    investors = {name for value in df["investors"] for name in investor_items(value, cfg)}
    money = amounts(df)
    metrics = [
        ("项目样本", df["project"].nunique()),
        ("一级分类", df["category"].nunique()),
        ("机构 / 投资方", len(investors)),
        ("有公开金额项目", int(money.notna().sum())),
        ("已披露金额合计", f"${money.sum(skipna=True):,.1f}M"),
    ]
    ink, muted = PALETTE["ink"], PALETTE["muted"]
    ax.text(0.02, 0.86, title, fontsize=24, fontweight="bold", color=ink, transform=ax.transAxes)
    ax.text(
        0.02,
        0.62,
        "市场格局维度：项目分类、融资额、机构参与、轮次、资金属性",
        fontsize=12,
        color=muted,
        transform=ax.transAxes,
    )
    x = 0.02
    for label, value in metrics:
        box = plt.Rectangle(
            (x, 0.16), 0.17, 0.28, transform=ax.transAxes, facecolor="#EEF5F1", edgecolor="#D4E1DC"
        )
        ax.add_patch(box)
        ax.text(
            x + 0.015,
            0.34,
            str(value),
            fontsize=18,
            fontweight="bold",
            color=ink,
            transform=ax.transAxes,
        )
        ax.text(x + 0.015, 0.22, label, fontsize=10, color=muted, transform=ax.transAxes)
        x += 0.19
    ax.text(
        0.02,
        0.03,
        "注：金额统计仅包含公开披露或可换算的项目；待 DD、传闻与用户线索不计入金额合计。",
        fontsize=9,
        color=muted,
        transform=ax.transAxes,
    )


def draw_category_bars(ax, df: pd.DataFrame, cfg: LandscapeConfig) -> None:
    setup_ax(ax, "A. 类别项目数与已披露融资额")
    stat = (
        df.assign(amount=amounts(df))
        .groupby("category", sort=False)
        .agg(projects=("project", "count"), capital=("amount", "sum"))
        .sort_values("projects")
    )
    y = np.arange(len(stat))
    ax.barh(y - 0.18, stat["projects"], height=0.32, color=PALETTE["teal"], label="项目数")
    top = ax.twiny()
    top.barh(y + 0.18, stat["capital"], height=0.32, color=PALETTE["yellow"], label="金额 $M")
    ax.set_yticks(y)
    ax.set_yticklabels([short(c, cfg, 16) for c in stat.index])
    ax.set_xlabel("项目数", color=PALETTE["muted"])
    top.set_xlabel("已披露金额 $M", color=PALETTE["muted"])
    top.tick_params(colors=PALETTE["muted"], labelsize=9)
    for spine in top.spines.values():
        spine.set_visible(False)


def draw_project_scatter(ax, df: pd.DataFrame, cfg: LandscapeConfig) -> None:
    setup_ax(ax, "B. 项目融资分布")
    known = df.assign(amount=amounts(df)).dropna(subset=["amount"])
    if known.empty:
        ax.text(0.5, 0.5, "无公开金额", ha="center", va="center", transform=ax.transAxes)
        return
    cats = unique_in_order(known["category"])
    for i, cat in enumerate(cats):
        part = known[known["category"] == cat].sort_values("amount")
        ys = np.array([i + jitter(name, 0.18) for name in part["project"]])
        sizes = np.clip(part["amount"].to_numpy() * 8, 80, 900)
        ax.scatter(part["amount"], ys, s=sizes, color=color(i), alpha=0.8, edgecolor="white")
        for x, yy, name in zip(part["amount"], ys, part["project"], strict=True):
            ax.text(x * 1.06, yy + 0.08, short(name, cfg, 18), fontsize=8, color=PALETTE["ink"])
    ax.set_xscale("symlog", linthresh=5)
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels([short(c, cfg, 16) for c in cats])
    ax.set_xlabel("融资金额 $M（对数轴）；未知金额不展示", color=PALETTE["muted"])


def draw_investor_heatmap(ax, df: pd.DataFrame, cfg: LandscapeConfig) -> None:
    setup_ax(ax, "C. 机构参与方向分布")
    cats = unique_in_order(df["category"])
    lists = [investor_items(value, cfg) for value in df["investors"]]
    top = heatmap_investors(lists, cfg)
    if not top:
        ax.text(0.5, 0.5, "无机构数据", ha="center", va="center", transform=ax.transAxes)
        return
    mat = np.zeros((len(top), len(cats)))
    for names, cat in zip(lists, df["category"], strict=True):
        for name in names:
            if name in top:
                mat[top.index(name), cats.index(str(cat))] += 1
    image = ax.imshow(mat, cmap="GnBu", aspect="auto", vmin=0)
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([short(c, cfg, 14) for c in cats], rotation=12, ha="right")
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([short(name, cfg, 18) for name in top])
    for i in range(len(top)):
        for j in range(len(cats)):
            if mat[i, j] > 0:
                text_color = "#FFFFFF" if mat[i, j] >= 2 else PALETTE["ink"]
                ax.text(
                    j,
                    i,
                    int(mat[i, j]),
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold",
                    color=text_color,
                )
    ax.text(
        0,
        -0.12,
        "数字 = 该机构在当前样本池中参与的项目数；入选规则：参与数前 10 + 配置中的关注名单。",
        transform=ax.transAxes,
        fontsize=8.5,
        color=PALETTE["muted"],
        ha="left",
        va="top",
    )
    plt.colorbar(image, ax=ax, fraction=0.035, pad=0.02)


def draw_investor_counts(ax, df: pd.DataFrame, cfg: LandscapeConfig) -> None:
    setup_ax(ax, "D. 机构参与项目数")
    counts = Counter(name for value in df["investors"] for name in investor_items(value, cfg))
    top = counts.most_common(10)[::-1]
    ax.barh(range(len(top)), [n for _, n in top], color=PALETTE["blue"])
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([short(name, cfg, 20) for name, _ in top])
    ax.set_xlabel("参与项目数", color=PALETTE["muted"])
    for i, (_, n) in enumerate(top):
        ax.text(n + 0.05, i, str(n), va="center", fontsize=9, color=PALETTE["ink"])


def draw_stage_distribution(ax, df: pd.DataFrame, cfg: LandscapeConfig) -> None:
    setup_ax(ax, "E. 融资轮次分布")
    stages = df["stage"].map(normalize_stage)
    pivot = pd.crosstab(df["category"], stages)
    order = [s for s in STAGE_ORDER if s in pivot.columns]
    pivot = pivot[order + [c for c in pivot.columns if c not in order]]
    bottom = np.zeros(len(pivot))
    labels = [short(c, cfg, 12) for c in pivot.index]
    for i, stage in enumerate(pivot.columns):
        values = pivot[stage].to_numpy()
        ax.bar(labels, values, bottom=bottom, label=stage, color=color(i), width=0.58)
        bottom += values
    ax.set_ylabel("项目数", color=PALETTE["muted"])
    ax.tick_params(axis="x", rotation=12)
    ax.legend(fontsize=7, loc="upper right", frameon=False)


def draw_investor_type(ax, df: pd.DataFrame, cfg: LandscapeConfig) -> None:
    setup_ax(ax, "F. 资金属性分布")
    counts = Counter(t for value in df["investor_types"] for t in type_items(value, cfg))
    if not counts:
        ax.text(0.5, 0.5, "无机构属性字段", ha="center", va="center", transform=ax.transAxes)
        return
    rows = counts.most_common()[::-1]
    ax.barh(
        range(len(rows)),
        [n for _, n in rows],
        color=[color(i) for i in range(len(rows))],
        height=0.52,
    )
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([label for label, _ in rows])
    ax.set_xlabel("出现次数", color=PALETTE["muted"])
    for i, (_, n) in enumerate(rows):
        ax.text(n + 0.08, i, str(n), va="center", fontsize=9, color=PALETTE["ink"])


def draw_market_map(ax, df: pd.DataFrame, cfg: LandscapeConfig) -> None:
    setup_ax(ax, "G. 二维市场地图")
    cats = unique_in_order(df["category"])
    x_pos = category_x(cats, cfg)
    for idx, row in enumerate(df.itertuples(index=False)):
        name = str(row.project)
        x = x_pos.get(str(row.category), 0.5) + jitter(name, 0.04)
        y = cfg.y_by_sub_type.get(str(row.sub_type), 0.5) + jitter(name + "/y", 0.03)
        fill = PALETTE[REGION_COLORS.get(str(row.region), "gray")]
        ax.scatter(x, y, s=95, color=fill, alpha=0.85, edgecolor="white")
        offset = 0.014 if idx % 2 == 0 else -0.014
        ax.text(x + 0.012, y + offset, short(name, cfg, 16), fontsize=7.6, color=PALETTE["ink"])
    x_ticks = cfg.x_ticks or [(x_pos[c], short(c, cfg, 14)) for c in cats]
    ax.set_xticks([pos for pos, _ in x_ticks])
    ax.set_xticklabels([label for _, label in x_ticks])
    ax.set_yticks([pos for pos, _ in cfg.y_ticks])
    ax.set_yticklabels([label for _, label in cfg.y_ticks])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def draw_project_table(ax, df: pd.DataFrame) -> None:
    ax.axis("off")
    ax.set_title(
        "H. 样本项目速览", loc="left", fontsize=13, fontweight="bold", color=PALETTE["ink"], pad=10
    )
    cols = ["project", "category", "stage", "amount_label", "source_status"]
    small = df[cols].head(12).fillna("待 DD").astype(str)
    small = small.apply(lambda col: col.map(lambda v: "\n".join(wrap(v, width=18)) or "待 DD"))
    small.columns = ["项目", "分类", "轮次", "金额", "信息状态"]
    table = ax.table(cellText=small.values, colLabels=small.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7.2)
    table.scale(1, 1.55)
    for (r, _c), cell in table.get_celld().items():
        cell.set_edgecolor("#DDE5E2")
        if r == 0:
            cell.set_facecolor("#EAF2EE")
            cell.set_text_props(weight="bold", color=PALETTE["ink"])
        else:
            cell.set_facecolor("#FFFFFF" if r % 2 else "#F6F9F7")


def load_table(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column in TEXT_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    if "amount_usd_m" not in df.columns:
        df["amount_usd_m"] = np.nan
    df[list(TEXT_COLUMNS)] = df[list(TEXT_COLUMNS)].fillna("")
    return df


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, help="bottom table as CSV")
    parser.add_argument("--output", required=True, help="output .png or .svg")
    parser.add_argument("--title", default="市场格局可视化")
    parser.add_argument("--config", help="JSON config (see config.example.json)")
    parser.add_argument("--format", choices=["png", "svg"], default=None)
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    plt.rcParams["font.sans-serif"] = [pick_font()]
    plt.rcParams["axes.unicode_minus"] = False
    df = load_table(args.input)

    fig = plt.figure(figsize=(22, 15.5), facecolor=PALETTE["paper"])
    grid = fig.add_gridspec(4, 6, height_ratios=[0.75, 1.35, 1.25, 1.45], hspace=0.48, wspace=0.4)
    draw_summary(fig.add_subplot(grid[0, :]), df, args.title, cfg)
    draw_category_bars(fig.add_subplot(grid[1, 0:2]), df, cfg)
    draw_project_scatter(fig.add_subplot(grid[1, 2:4]), df, cfg)
    draw_investor_heatmap(fig.add_subplot(grid[1, 4:6]), df, cfg)
    draw_investor_counts(fig.add_subplot(grid[2, 0:2]), df, cfg)
    draw_stage_distribution(fig.add_subplot(grid[2, 2:4]), df, cfg)
    draw_investor_type(fig.add_subplot(grid[2, 4:6]), df, cfg)
    draw_market_map(fig.add_subplot(grid[3, 0:3]), df, cfg)
    draw_project_table(fig.add_subplot(grid[3, 3:6]), df)

    fmt = args.format or args.output.rsplit(".", 1)[-1].lower()
    fig.savefig(args.output, dpi=220, bbox_inches="tight", facecolor=PALETTE["paper"], format=fmt)


if __name__ == "__main__":
    main()
