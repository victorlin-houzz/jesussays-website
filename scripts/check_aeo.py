#!/usr/bin/env python3
"""Validate content pages meet AEO requirements. Exit 1 if any fail."""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path


class PageChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags: set[str] = set()
        self.schema_types: set[str] = set()
        self.has_canonical = False
        self.has_meta_description = False
        self.has_app_store_link = False
        self.has_faq_h2 = False
        self._in_script_ld = False
        self._script_buf = ""
        self._in_h2 = False
        self._h2_buf = ""
        self._first_p_words = 0
        self._first_p_done = False
        self._in_first_p = False

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        self.tags.add(tag)
        if tag == "h2":
            self._in_h2 = True
            self._h2_buf = ""
        elif tag == "link" and attrs_d.get("rel") == "canonical" and attrs_d.get("href"):
            self.has_canonical = True
        elif tag == "meta" and attrs_d.get("name") == "description" and attrs_d.get("content"):
            self.has_meta_description = True
        elif tag == "a" and "apps.apple.com/us/app/jesus-says-now" in attrs_d.get("href", ""):
            self.has_app_store_link = True
        elif tag == "script" and attrs_d.get("type") == "application/ld+json":
            self._in_script_ld = True
            self._script_buf = ""
        elif tag == "p" and not self._first_p_done and not self._in_first_p:
            self._in_first_p = True

    def handle_endtag(self, tag):
        if tag == "script" and self._in_script_ld:
            self._in_script_ld = False
            try:
                data = json.loads(self._script_buf)
                items = data.get("@graph", [data]) if isinstance(data, dict) else data
                for item in (items if isinstance(items, list) else [items]):
                    self.schema_types.add(item.get("@type", ""))
            except Exception:
                pass
        elif tag == "h2" and self._in_h2:
            self._in_h2 = False
            text = self._h2_buf.strip().lower()
            if "frequently asked" in text or "faq" in text:
                self.has_faq_h2 = True
        elif tag == "p" and self._in_first_p:
            self._in_first_p = False
            self._first_p_done = True

    def handle_data(self, data):
        if self._in_script_ld:
            self._script_buf += data
        elif self._in_h2:
            self._h2_buf += data
        elif self._in_first_p:
            self._first_p_words += len(data.split())


def check(path: Path) -> list[str]:
    p = PageChecker()
    p.feed(path.read_text(encoding="utf-8"))
    issues = []
    if "h1" not in p.tags:
        issues.append("missing <h1>")
    if not p.has_canonical:
        issues.append("missing canonical link")
    if not p.has_meta_description:
        issues.append("missing meta description")
    if "Article" not in p.schema_types:
        issues.append("missing Article JSON-LD")
    if "FAQPage" not in p.schema_types:
        issues.append("missing FAQPage JSON-LD")
    if not p.has_app_store_link:
        issues.append("missing App Store link (jesus-says-now)")
    if not p.has_faq_h2:
        issues.append("missing FAQ section h2")
    if p._first_p_words > 80:
        issues.append(f"direct answer too long ({p._first_p_words} words, max 80)")
    if p._first_p_words < 10:
        issues.append(f"direct answer missing or too short ({p._first_p_words} words)")
    return issues


if __name__ == "__main__":
    skip = {"index.html", "keyword-clusters.html"}
    pages = sorted(p for p in Path("content").glob("*.html") if p.name not in skip)
    failed = 0
    for page in pages:
        issues = check(page)
        status = "PASS" if not issues else "FAIL"
        print(f"{status}  {page.name}")
        for issue in issues:
            print(f"      • {issue}")
        if issues:
            failed += 1
    total = len(pages)
    print(f"\n{total - failed}/{total} pages pass AEO checks.")
    sys.exit(1 if failed else 0)
