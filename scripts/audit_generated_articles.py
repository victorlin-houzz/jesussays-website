#!/usr/bin/env python3
"""Audit drafted opportunity articles for SEO/AEO, safety, and CTA quality."""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from manage_opportunities import OPPORTUNITIES_PATH, load_opportunities, write_opportunities

CONTENT_DIR = Path("content")
SENSITIVE_TERMS = {
    "addiction",
    "anxiety",
    "cancer",
    "depression",
    "grief",
    "healing",
    "hopelessness",
    "mental health",
    "miscarriage",
    "surgery",
    "suicide",
    "trauma",
}
CARE_TERMS = {
    "professional",
    "medical",
    "doctor",
    "counselor",
    "pastor",
    "emergency",
    "crisis",
    "988",
}
FORBIDDEN_PROMISES = [
    "guaranteed healing",
    "guarantee healing",
    "will heal you",
    "will cure",
    "cure your",
    "fix your depression",
    "replace therapy",
    "replace medical",
]
PLACEHOLDER_PATTERNS = [
    "[title]",
    "[description]",
    "[q1]",
    "[a1",
    "slug.html",
    "{{today}}",
    "{{keyword}}",
]


class ArticleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text_parts: list[str] = []
        self.h1_count = 0
        self.h2_texts: list[str] = []
        self._capture_h2 = False
        self._h2_buf: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"head", "script", "style"}:
            self._skip_depth += 1
            return
        if tag == "h1":
            self.h1_count += 1
        if tag == "h2":
            self._capture_h2 = True
            self._h2_buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"head", "script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag == "h2" and self._capture_h2:
            self._capture_h2 = False
            self.h2_texts.append(" ".join(self._h2_buf).strip())

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self.text_parts.append(data)
        if self._capture_h2:
            self._h2_buf.append(data)

    @property
    def text(self) -> str:
        return " ".join(part.strip() for part in self.text_parts if part.strip())


def is_sensitive(row: dict, text: str) -> bool:
    haystack = " ".join(
        [
            row.get("primary_keyword", ""),
            row.get("jesus_says_title", ""),
            row.get("user_need", ""),
            text[:3000],
        ]
    ).lower()
    return any(term in haystack for term in SENSITIVE_TERMS)


def audit_row(row: dict) -> list[str]:
    slug = row["target_slug"]
    path = CONTENT_DIR / f"{slug}.html"
    issues: list[str] = []
    if not path.exists():
        return [f"missing generated file: {path}"]

    html = path.read_text(encoding="utf-8")
    lower = html.lower()
    parser = ArticleTextParser()
    parser.feed(html)
    text = parser.text
    text_lower = text.lower()

    if parser.h1_count != 1:
        issues.append(f"expected exactly one h1, found {parser.h1_count}")
    if "Frequently Asked Questions" not in parser.h2_texts:
        issues.append("missing FAQ h2")
    if f'utm_campaign=content-{slug}' not in html:
        issues.append("missing matching content UTM campaign")
    if "apps.apple.com/us/app/jesus-says-now" not in html:
        issues.append("missing App Store CTA")
    if '<meta property="og:type" content="article"' not in html:
        issues.append("missing article og:type")
    if '"FAQPage"' not in html or '"Article"' not in html:
        issues.append("missing Article or FAQPage JSON-LD")
    if row["source_site"].lower() in text_lower or row["source_url"].lower() in lower:
        issues.append("mentions competitor/source in article body")
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.lower() in lower:
            issues.append(f"placeholder leaked: {pattern}")
    for phrase in FORBIDDEN_PROMISES:
        if phrase in text_lower:
            issues.append(f"unsafe promise phrase: {phrase}")
    if is_sensitive(row, text) and not any(term in text_lower for term in CARE_TERMS):
        issues.append("sensitive topic lacks care/professional-help note")
    body_words = len(text.split())
    if body_words < 650:
        issues.append(f"article appears too short ({body_words} words)")
    if body_words > 1800:
        issues.append(f"article appears too long ({body_words} words)")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", default="drafted")
    parser.add_argument("--mark-published", action="store_true")
    parser.add_argument("--id", action="append", default=[])
    args = parser.parse_args()

    rows = load_opportunities(OPPORTUNITIES_PATH)
    wanted = set(args.id)
    selected = [
        row
        for row in rows
        if (not wanted and row["status"] == args.status)
        or (wanted and (row["id"] in wanted or row["target_slug"] in wanted))
    ]
    failed = 0
    for row in selected:
        issues = audit_row(row)
        if issues:
            failed += 1
            print(f"FAIL {row['id']} {row['target_slug']}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"PASS {row['id']} {row['target_slug']}")
            if args.mark_published:
                row["status"] = "published"
                row["published_at"] = row.get("published_at") or __import__("datetime").date.today().isoformat()

    if args.mark_published and failed == 0:
        write_opportunities(rows, OPPORTUNITIES_PATH)
    print(f"\n{len(selected) - failed}/{len(selected)} drafted articles passed audit.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
