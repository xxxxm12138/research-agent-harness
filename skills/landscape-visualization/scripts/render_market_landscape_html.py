#!/usr/bin/env python3
"""Render a mapping bottom table as a self-contained interactive HTML landscape.

Usage:
    python render_market_landscape_html.py --input data.csv --output out.html \
        --title "示例赛道市场格局" [--config landscape.config.json]

Requires pandas (``pip install -e ".[viz]"``). The page layout lives in
``landscape_template.html``; this script only cleans the data and embeds it. All
text from the CSV is escaped before it reaches the page.
"""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from _landscape_config import (
    LandscapeConfig,
    category_x,
    investor_items,
    load_config,
    type_items,
    unique_in_order,
)

TEMPLATE = Path(__file__).with_name("landscape_template.html")
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


def clean_records(df: pd.DataFrame, cfg: LandscapeConfig) -> list[dict[str, Any]]:
    df = df.copy()
    for column in TEXT_COLUMNS:
        if column not in df.columns:
            df[column] = ""
        df[column] = df[column].fillna("").astype(str)
    raw_amounts = df["amount_usd_m"] if "amount_usd_m" in df.columns else None
    numeric = pd.to_numeric(raw_amounts, errors="coerce") if raw_amounts is not None else None
    records = []
    for index, row in enumerate(df[list(TEXT_COLUMNS)].to_dict(orient="records")):
        amount = None if numeric is None else numeric.iloc[index]
        row["amount_usd_m"] = None if amount is None or math.isnan(amount) else float(amount)
        row["investor_list"] = investor_items(row["investors"], cfg)
        row["investor_type_list"] = type_items(row["investor_types"], cfg)
        records.append(row)
    return records


def build_payload(df: pd.DataFrame, cfg: LandscapeConfig) -> dict[str, Any]:
    records = clean_records(df, cfg)
    categories = unique_in_order(r["category"] for r in records)
    x_map = category_x(categories, cfg)
    x_ticks = cfg.x_ticks or [(x_map[c], c) for c in categories]
    return {
        "records": records,
        "focus": cfg.heatmap_focus_investors,
        "exclude": sorted(cfg.heatmap_exclude_investors),
        "shortLabels": cfg.short_labels,
        "xMap": x_map,
        "yMap": cfg.y_by_sub_type,
        "xTicks": [list(tick) for tick in x_ticks],
        "yTicks": [list(tick) for tick in cfg.y_ticks],
    }


def render_html(title: str, payload: dict[str, Any], template: str | None = None) -> str:
    """Fill the template. JSON is embedded in a data block with ``</`` escaped."""
    page = template if template is not None else TEMPLATE.read_text(encoding="utf-8")
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return page.replace("__TITLE__", html.escape(title)).replace("__DATA__", data)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, help="bottom table as CSV")
    parser.add_argument("--output", required=True, help="output .html")
    parser.add_argument("--title", default="市场格局可视化")
    parser.add_argument("--config", help="JSON config (see config.example.json)")
    args = parser.parse_args(argv)

    payload = build_payload(pd.read_csv(args.input), load_config(args.config))
    Path(args.output).write_text(render_html(args.title, payload), encoding="utf-8")


if __name__ == "__main__":
    main()
