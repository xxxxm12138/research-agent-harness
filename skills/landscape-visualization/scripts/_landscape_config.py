"""Shared configuration and data helpers for the market-landscape renderers.

Investor focus lists, label overrides and market-map coordinates are data, not code.
They live in a JSON config (see ``config.example.json``) so the renderers contain no
project or institution names, and so a chart's inclusion rules are written down next
to the data they were applied to.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_IGNORE = ("待 DD", "待DD", "NA", "nan", "")
DEFAULT_TYPE_LABELS = {
    "财务VC": "财务 VC",
    "产业资本": "产业 / 战略",
    "战略资本": "产业 / 战略",
    "政府基金": "政府基金",
    "国资": "政府基金",
    "天使": "个人 / 天使",
    "个人投资人": "个人 / 天使",
    "大厂参照": "大厂参照",
}


@dataclass
class LandscapeConfig:
    ignore_investors: set[str] = field(default_factory=lambda: set(DEFAULT_IGNORE))
    canonical_investors: dict[str, str] = field(default_factory=dict)
    heatmap_focus_investors: list[str] = field(default_factory=list)
    heatmap_exclude_investors: set[str] = field(default_factory=set)
    short_labels: dict[str, str] = field(default_factory=dict)
    type_labels: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_TYPE_LABELS))
    x_by_category: dict[str, float] = field(default_factory=dict)
    y_by_sub_type: dict[str, float] = field(default_factory=dict)
    x_ticks: list[tuple[float, str]] = field(default_factory=list)
    y_ticks: list[tuple[float, str]] = field(default_factory=list)


def _ticks(items: Iterable[Any]) -> list[tuple[float, str]]:
    return [(float(pos), str(label)) for pos, label in items]


def load_config(path: str | Path | None) -> LandscapeConfig:
    """Load a JSON config; missing keys fall back to neutral defaults."""
    if path is None:
        return LandscapeConfig()
    data: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    cfg = LandscapeConfig()
    if "ignore_investors" in data:
        cfg.ignore_investors = set(data["ignore_investors"])
    cfg.canonical_investors = dict(data.get("canonical_investors", {}))
    cfg.heatmap_focus_investors = list(data.get("heatmap_focus_investors", []))
    cfg.heatmap_exclude_investors = set(data.get("heatmap_exclude_investors", []))
    cfg.short_labels = dict(data.get("short_labels", {}))
    cfg.type_labels = {**DEFAULT_TYPE_LABELS, **data.get("type_labels", {})}
    market_map = data.get("market_map", {})
    cfg.x_by_category = {k: float(v) for k, v in market_map.get("x_by_category", {}).items()}
    cfg.y_by_sub_type = {k: float(v) for k, v in market_map.get("y_by_sub_type", {}).items()}
    cfg.x_ticks = _ticks(market_map.get("x_ticks", []))
    cfg.y_ticks = _ticks(market_map.get("y_ticks", []))
    return cfg


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() == ""


def split_multi(value: Any) -> list[str]:
    """Split a multi-value cell on ``;``, ``,`` or ``、``."""
    if is_blank(value):
        return []
    text = str(value).replace("、", ";").replace(",", ";").replace("，", ";")
    return [item.strip() for item in text.split(";") if item.strip()]


def investor_items(value: Any, cfg: LandscapeConfig) -> list[str]:
    items = []
    for item in split_multi(value):
        item = cfg.canonical_investors.get(item, item)
        if item not in cfg.ignore_investors:
            items.append(item)
    return items


def type_items(value: Any, cfg: LandscapeConfig) -> list[str]:
    items = []
    for item in split_multi(value):
        item = cfg.type_labels.get(item, item)
        if item not in cfg.ignore_investors:
            items.append(item)
    return items


def heatmap_investors(
    investor_lists: Iterable[list[str]], cfg: LandscapeConfig, limit: int = 22
) -> list[str]:
    """Top-10 investors by deal count, then the documented focus list, capped at ``limit``."""
    counts = Counter(name for names in investor_lists for name in names)

    def focus_rank(name: str) -> int:
        focus = cfg.heatmap_focus_investors
        return focus.index(name) if name in focus else len(focus)

    ranked = sorted(
        (name for name in counts if name not in cfg.heatmap_exclude_investors),
        key=lambda name: (-counts[name], focus_rank(name), name),
    )
    selected = ranked[:10]
    for name in cfg.heatmap_focus_investors:
        if len(selected) >= limit:
            break
        if counts.get(name) and name not in selected and name not in cfg.heatmap_exclude_investors:
            selected.append(name)
    return selected[:limit]


def category_x(categories: list[str], cfg: LandscapeConfig) -> dict[str, float]:
    """Configured x position per category; unconfigured categories are spread evenly."""
    n = max(1, len(categories))
    return {
        category: cfg.x_by_category.get(category, (index + 0.5) / n)
        for index, category in enumerate(categories)
    }


def unique_in_order(values: Iterable[Any]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if not is_blank(value) and str(value) not in seen:
            seen.append(str(value))
    return seen
