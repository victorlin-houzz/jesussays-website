#!/usr/bin/env python3
"""Validate Faith Library pages: AEO structure, editorial quality, and site registration.

Checks every article listed in _data/library.json for search/answer-engine metadata,
then applies the editorial rules in scripts/content_rules.py (verbatim KJV quotes,
banned positioning, care notes, near-duplicate text) and confirms that every file in
content/ is either a catalog article, a registered redirect stub, or the index.
Exit 1 if anything fails.
"""
import json
import sys
import xml.etree.ElementTree as ET
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
        self.has_robots_meta = False
        self.has_og_title = False
        self.has_og_description = False
        self.has_og_type = False
        self.has_og_url = False
        self.has_og_image = False
        self.has_twitter_card = False
        self.has_date_published = False
        self.has_date_modified = False
        self.has_publisher = False
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
        elif tag == "meta" and attrs_d.get("name") == "robots" and attrs_d.get("content"):
            self.has_robots_meta = True
        elif tag == "meta" and attrs_d.get("property") == "og:title" and attrs_d.get("content"):
            self.has_og_title = True
        elif tag == "meta" and attrs_d.get("property") == "og:description" and attrs_d.get("content"):
            self.has_og_description = True
        elif tag == "meta" and attrs_d.get("property") == "og:type" and attrs_d.get("content"):
            self.has_og_type = True
        elif tag == "meta" and attrs_d.get("property") == "og:url" and attrs_d.get("content"):
            self.has_og_url = True
        elif tag == "meta" and attrs_d.get("property") == "og:image" and attrs_d.get("content"):
            self.has_og_image = True
        elif tag == "meta" and attrs_d.get("name") == "twitter:card" and attrs_d.get("content"):
            self.has_twitter_card = True
        elif tag == "a" and "apps.apple.com/us/app/jesus-says-daily-reflection/id6756906208" in attrs_d.get("href", ""):
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
                    if item.get("@type") == "Article":
                        self.has_date_published = bool(item.get("datePublished"))
                        self.has_date_modified = bool(item.get("dateModified"))
                        self.has_publisher = bool(item.get("publisher"))
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


def check_site_files(catalog: dict, redirects: dict) -> list[str]:
    issues = []
    if not Path("assets/og-image.png").exists():
        issues.append("missing assets/og-image.png referenced by every page")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = {loc.text for loc in ET.parse("sitemap.xml").findall("s:url/s:loc", ns)}
    if "https://jesussays.app/content/" not in urls:
        issues.append("sitemap missing canonical /content/ URL")
    for a in catalog["articles"]:
        if f"https://jesussays.app/content/{a['slug']}.html" not in urls:
            issues.append(f"sitemap missing {a['slug']}")
    for old in redirects:
        if f"https://jesussays.app/content/{old}.html" in urls:
            issues.append(f"sitemap lists redirect stub {old}")
    for page in ["index.html", "download.html", "about.html", "404.html", "play/still-waters/index.html", "content/index.html",
                 "author/jesus-says-team/index.html"]:
        text = Path(page).read_text(encoding="utf-8")
        if "jesus-says-now" in text:
            issues.append(f"{page}: old App Store slug jesus-says-now")
        if "apple-itunes-app" not in text:
            issues.append(f"{page}: missing Smart App Banner meta")
    return issues


def check(path: Path) -> list[str]:
    p = PageChecker()
    text = path.read_text(encoding="utf-8")
    p.feed(text)
    has_faq = '<section class="faq">' in text
    issues = []
    if "h1" not in p.tags:
        issues.append("missing <h1>")
    if not p.has_canonical:
        issues.append("missing canonical link")
    if not p.has_meta_description:
        issues.append("missing meta description")
    if not p.has_robots_meta:
        issues.append("missing robots meta")
    if not all([p.has_og_title, p.has_og_description, p.has_og_type, p.has_og_url, p.has_og_image, p.has_twitter_card]):
        issues.append("missing complete social preview metadata")
    if "Article" not in p.schema_types:
        issues.append("missing Article JSON-LD")
    else:
        if not p.has_date_published:
            issues.append("missing Article datePublished")
        if not p.has_date_modified:
            issues.append("missing Article dateModified")
        if not p.has_publisher:
            issues.append("missing Article publisher")
    if has_faq and "FAQPage" not in p.schema_types:
        issues.append("missing FAQPage JSON-LD")
    if not p.has_app_store_link:
        issues.append("missing App Store link (jesus-says-daily-reflection)")
    if has_faq and not p.has_faq_h2:
        issues.append("missing FAQ section h2")
    if p._first_p_words > 80:
        issues.append(f"direct answer too long ({p._first_p_words} words, max 80)")
    if p._first_p_words < 10:
        issues.append(f"direct answer missing or too short ({p._first_p_words} words)")
    return issues


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_site
    import content_rules

    catalog = build_site.load_catalog()
    redirects = json.loads(build_site.REDIRECTS.read_text(encoding="utf-8"))
    allowed = {a["slug"] for a in catalog["articles"]}
    failed = 0

    def report(label: str, issues: list[str]) -> None:
        nonlocal failed
        print(f"{'PASS' if not issues else 'FAIL'}  {label}")
        for issue in issues:
            print(f"      • {issue}")
        failed += bool(issues)

    bodies = {}
    for a in catalog["articles"]:
        path = Path("content") / f"{a['slug']}.html"
        if not path.exists():
            report(path.name, ["file missing"])
            continue
        page = path.read_text(encoding="utf-8")
        body = build_site.extract_body(page)
        bodies[a["slug"]] = body
        report(path.name, check(path) + content_rules.check_body(a["slug"], body, allowed))

    pages = {a["slug"]: bodies.get(a["slug"], "") for a in catalog["articles"]}
    report("site registration and links", build_site.validate(catalog, redirects, pages))
    report("site files", check_site_files(catalog, redirects))
    report("near-duplicate content", content_rules.near_duplicates(bodies))

    total = len(catalog["articles"])
    print(f"\n{total} articles, {len(redirects)} redirect stubs checked.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
