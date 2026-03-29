#!/usr/bin/env python3
"""Dependency-free validation for this static site.

Checks:
1) HTML parseability for index.html
2) Required InterviewIQ DOM anchors
3) Local href/src references resolve on disk
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

REQUIRED_IDS = {
    "iq-section-select",
    "iq-role",
    "iq-format",
    "iq-resume",
    "iq-jd",
    "iq-generate-questions",
    "iq-question-pills",
    "iq-active-question",
    "iq-answer-input",
    "iq-generate-answer",
    "iq-ai-response",
}


class Validator(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.missing_paths: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        node_id = attrs_dict.get("id")
        if node_id:
            self.ids.add(node_id)

        for key in ("href", "src"):
            value = attrs_dict.get(key)
            if not value:
                continue
            if value.startswith(("http://", "https://", "mailto:", "#", "tel:", "javascript:", "data:")):
                continue
            rel = unquote(value.split("?")[0].split("#")[0].lstrip("/"))
            if not rel:
                continue
            target = ROOT / rel
            if not target.exists():
                self.missing_paths.append(f"{key}='{value}' -> {rel}")


def main() -> int:
    if not INDEX.exists():
        print("ERROR: index.html not found")
        return 1

    parser = Validator()
    parser.feed(INDEX.read_text(encoding="utf-8", errors="ignore"))
    parser.close()

    missing_ids = sorted(REQUIRED_IDS - parser.ids)
    if missing_ids:
        print("ERROR: missing required InterviewIQ ids:")
        for item in missing_ids:
            print(f"  - {item}")

    if parser.missing_paths:
        print("ERROR: unresolved local asset paths in index.html:")
        for item in parser.missing_paths:
            print(f"  - {item}")

    if missing_ids or parser.missing_paths:
        return 1

    print("PASS: index.html parsed, required InterviewIQ ids present, and local paths resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
