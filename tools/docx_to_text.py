#!/usr/bin/env python3
"""Convert a .docx file to plain text, using only the standard library.

Keeps document order, marks headings with ``#`` and renders tables as pipe rows, so
call-report and interview notes stored as Word files can be read by an agent.

    python tools/docx_to_text.py notes.docx            # writes notes.txt
    python tools/docx_to_text.py notes.docx out.txt
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_HEADING = re.compile(r"(?:heading|标题)\s*(\d)", re.IGNORECASE)


def _text(element: ET.Element) -> str:
    parts: list[str] = []
    for node in element.iter():
        if node.tag == W + "t" and node.text:
            parts.append(node.text)
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            parts.append("\n")
    return "".join(parts).strip()


def _style_names(archive: zipfile.ZipFile) -> dict[str, str]:
    """Map style ids to style names (Word stores built-in names such as ``heading 1``)."""
    if "word/styles.xml" not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read("word/styles.xml"))
    names: dict[str, str] = {}
    for style in root.iter(W + "style"):
        name = style.find(W + "name")
        if name is not None:
            names[style.get(W + "styleId", "")] = name.get(W + "val", "")
    return names


def _heading_level(paragraph: ET.Element, styles: dict[str, str]) -> int | None:
    style = paragraph.find(f"{W}pPr/{W}pStyle")
    if style is None:
        return None
    style_id = style.get(W + "val", "")
    match = _HEADING.search(styles.get(style_id, "")) or _HEADING.search(style_id)
    return int(match.group(1)) if match else None


def convert(path: Path | str) -> str:
    """Return the text of a .docx document, paragraphs and tables in document order."""
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
        styles = _style_names(archive)
    body = root.find(W + "body")
    blocks: list[str] = []
    for child in body if body is not None else []:
        if child.tag == W + "p":
            text = _text(child)
            if text:
                level = _heading_level(child, styles)
                blocks.append(f"{'#' * level} {text}" if level else text)
        elif child.tag == W + "tbl":
            rows = []
            for row in child.iter(W + "tr"):
                cells = [_text(cell).replace("\n", " ") for cell in row.findall(W + "tc")]
                if any(cells):
                    rows.append("| " + " | ".join(cells) + " |")
            if rows:
                blocks.append("\n".join(rows))
    return "\n\n".join(blocks) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert .docx to plain text")
    parser.add_argument("docx", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    args = parser.parse_args(argv)
    output = args.output or args.docx.with_suffix(".txt")
    text = convert(args.docx)
    output.write_text(text, encoding="utf-8")
    print(f"{args.docx} -> {output} ({len(text)} characters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
