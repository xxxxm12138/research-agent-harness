from __future__ import annotations

import importlib.util
import zipfile

import pytest

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


@pytest.fixture(scope="module")
def docx_to_text(root):
    spec = importlib.util.spec_from_file_location(
        "docx_to_text", root / "tools" / "docx_to_text.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(text: str) -> str:
    return f"<w:r><w:t>{text}</w:t></w:r>"


def _make_docx(path, body: str, styles: str) -> None:
    document = f'<w:document xmlns:w="{W_NS}"><w:body>{body}</w:body></w:document>'
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", f'<w:styles xmlns:w="{W_NS}">{styles}</w:styles>')


def test_docx_to_text_keeps_order_headings_and_tables(tmp_path, docx_to_text):
    body = (
        '<w:p><w:pPr><w:pStyle w:val="1"/></w:pPr>' + _run("公司业务") + "</w:p>"
        "<w:p>" + _run("团队 10 人") + "<w:r><w:tab/><w:t>两地办公</w:t></w:r></w:p>"
        "<w:p></w:p>"
        "<w:tbl>"
        "<w:tr><w:tc><w:p>"
        + _run("轮次")
        + "</w:p></w:tc><w:tc><w:p>"
        + _run("金额")
        + "</w:p></w:tc></w:tr>"
        "<w:tr><w:tc><w:p>"
        + _run("天使")
        + "</w:p></w:tc><w:tc><w:p>"
        + _run("500 万")
        + "</w:p></w:tc></w:tr>"
        "</w:tbl>"
        "<w:p>" + _run("结尾") + "</w:p>"
    )
    styles = '<w:style w:styleId="1"><w:name w:val="heading 2"/></w:style>'
    path = tmp_path / "notes.docx"
    _make_docx(path, body, styles)
    assert docx_to_text.convert(path) == (
        "## 公司业务\n\n团队 10 人\t两地办公\n\n| 轮次 | 金额 |\n| 天使 | 500 万 |\n\n结尾\n"
    )


def test_docx_to_text_cli_writes_txt(tmp_path, docx_to_text):
    path = tmp_path / "a.docx"
    _make_docx(path, "<w:p>" + _run("hello") + "</w:p>", "")
    assert docx_to_text.main([str(path)]) == 0
    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "hello\n"
