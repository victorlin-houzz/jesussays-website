#!/usr/bin/env python3
"""Rebuild the Faith Library and shared site chrome from `_data/library.json`.

The catalog is the single source of truth for which articles exist. This script:
  * re-renders every catalog article with the shared head, nav, CTA, related links and footer,
    keeping the article body between the `<!-- article:body -->` markers untouched;
  * regenerates JSON-LD (Article, FAQPage from the visible FAQ, BreadcrumbList);
  * writes content/index.html, sitemap.xml and llms.txt;
  * writes redirect stubs for retired URLs listed in `_data/redirects.json`;
  * refreshes the nav/footer blocks (between `<!-- site:nav -->` / `<!-- site:footer -->` markers)
    on hand-authored pages;
  * fails if any page in content/ is not registered in the catalog or the redirect map.

Usage:
  python3 scripts/build_site.py                 # rebuild everything
  python3 scripts/build_site.py --ingest DIR    # first replace bodies/metadata from DIR/<slug>.html + .json
  python3 scripts/build_site.py --check         # validate only, write nothing
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_chrome as chrome  # noqa: E402
from site_analytics import with_analytics

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "_data" / "library.json"
REDIRECTS = ROOT / "_data" / "redirects.json"
AUTHOR = ROOT / "_data" / "author.json"
CONTENT = ROOT / "content"
SITE = chrome.SITE

HAND_PAGES = {  # path -> (is_home, nav key)
    "index.html": (True, None),
    "download.html": (False, None),
    "about.html": (False, None),
    "404.html": (False, None),
    "play/still-waters/index.html": (False, "still-waters"),
}

BODY_START, BODY_END = "<!-- article:body -->", "<!-- /article:body -->"
STUB_MARK = "<!-- redirect-stub -->"

BACK_SVG = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>')

CTA_HEADINGS = {
    "anxiety-fear-peace": "When worry is loud, start with one verse.",
    "hard-seasons": "Bring what you're carrying to Scripture, one day at a time.",
    "healing-hope": "Keep hope close, one verse at a time.",
    "prayer-devotion": "Two quiet minutes with God, every day.",
    "faith-purpose": "Walk with the words of Jesus every day.",
    "confession-forgiveness": "Come back to grace with one honest prayer a day.",
    "relationships": "Bring the people you love to God each day.",
    "compare": "Try Jesus Says for yourself.",
}
RELATED_HEADINGS = {
    "anxiety-fear-peace": "More for anxious days",
    "hard-seasons": "More for hard seasons",
    "healing-hope": "More on healing and hope",
    "prayer-devotion": "More on prayer and devotion",
    "faith-purpose": "More on faith and the words of Jesus",
    "confession-forgiveness": "More on confession and forgiveness",
    "relationships": "More on relationships",
    "compare": "More app comparisons",
}
CTA_BODY = ("Jesus Says: Daily Reflection gives you one verse, one reflection, one prayer, and one step for today. "
            "Speak or type what you're carrying and receive Scripture and a prayer you can return to.")
CTA_SMALL = "Free on iPhone and iPad · 7 days of full access, then Plus"


# ── helpers ──────────────────────────────────────────────────────────────────
def load_catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def load_author() -> dict:
    return json.loads(AUTHOR.read_text(encoding="utf-8"))


def reviewer_of(author: dict) -> dict | None:
    """The named person who reviews the guides, once `_data/author.json` names one."""
    r = author.get("reviewer") or {}
    return r if r.get("name", "").strip() else None


def person_node(r: dict) -> dict:
    node = {
        "@type": "Person",
        "@id": f"{SITE}{chrome.AUTHOR_PATH}#reviewer",
        "name": r["name"].strip(),
        "url": f"{SITE}{chrome.AUTHOR_PATH}",
        "worksFor": {"@id": chrome.ORG_ID},
    }
    if r.get("job_title"):
        node["jobTitle"] = r["job_title"]
    if r.get("same_as"):
        node["sameAs"] = r["same_as"]
    return node


def byline(author: dict) -> str:
    team = f'<span>By <a href="{chrome.AUTHOR_PATH}" rel="author">{chrome.esc(author["name"])}</a></span>'
    how = f'<a href="{chrome.AUTHOR_PATH}#how-we-write">AI-assisted</a>'
    r = reviewer_of(author)
    if r:
        return f'{team}<span>{how}, reviewed by <a href="{chrome.AUTHOR_PATH}#reviewer">{chrome.esc(r["name"].strip())}</a></span>'
    return f'{team}<span><a href="{chrome.AUTHOR_PATH}#how-we-write">AI-assisted, reviewed by a person</a></span>'


def human_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def article_url(slug: str) -> str:
    return f"{SITE}/content/{slug}.html"


def extract_body(page: str) -> str:
    if BODY_START in page:
        return page.split(BODY_START, 1)[1].split(BODY_END, 1)[0].strip("\n")
    raise ValueError("article body markers not found")


def parse_faq(body: str) -> list[tuple[str, str]]:
    m = re.search(r'<section class="faq">(.*?)</section>', body, re.S)
    if not m:
        return []
    parts = re.split(r"<h3[^>]*>(.*?)</h3>", m.group(1), flags=re.S)
    pairs = []
    for i in range(1, len(parts) - 1, 2):
        q, a = strip_tags(parts[i]), strip_tags(parts[i + 1])
        if q and a:
            pairs.append((q, a))
    return pairs


def home_faq_ld(page: str) -> str:
    """FAQPage JSON-LD mirroring the visible <details class="faq-item"> list on the homepage."""
    items = re.findall(r'<details class="faq-item"[^>]*>\s*<summary>(.*?)</summary>\s*<div class="ans">(.*?)</div>', page, re.S)
    graph = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": f"{SITE}/#faq",
        "mainEntity": [
            {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in items
        ],
    }
    return ("<!-- site:faq-ld -->\n  <script type=\"application/ld+json\">\n"
            + json.dumps(graph, ensure_ascii=False, indent=2) + "\n  </script>\n  <!-- /site:faq-ld -->")


def replace_block(page: str, name: str, block: str) -> str:
    pattern = re.compile(rf"<!-- site:{name} -->.*?<!-- /site:{name} -->", re.S)
    if not pattern.search(page):
        raise ValueError(f"missing <!-- site:{name} --> markers")
    return pattern.sub(lambda _: block, page, count=1)


# ── article pages ────────────────────────────────────────────────────────────
def render_article(a: dict, body: str, catalog: dict, author: dict) -> str:
    by_slug = {x["slug"]: x for x in catalog["articles"]}
    cats = {c["id"]: c for c in catalog["categories"]}
    cat = cats[a["category"]]
    url = article_url(a["slug"])
    faq = parse_faq(body)
    reviewer = reviewer_of(author)

    graph = [
        chrome.organization_node(),
        chrome.website_node(),
        *([person_node(reviewer)] if reviewer else []),
        {
            "@type": "Article",
            "@id": f"{url}#article",
            "headline": a["h1"],
            "description": a["description"],
            "datePublished": a["published"],
            "dateModified": a["modified"],
            "author": {"@id": person_node(reviewer)["@id"]} if reviewer else {"@id": chrome.ORG_ID},
            "publisher": {"@id": chrome.ORG_ID},
            "image": chrome.OG_IMAGE,
            "mainEntityOfPage": url,
            "isPartOf": {"@id": chrome.WEBSITE_ID},
            "articleSection": cat["name"],
            "inLanguage": "en-US",
        },
        chrome.breadcrumb_node([("Home", f"{SITE}/"), ("Faith Library", f"{SITE}/content/"), (a["h1"], url)]),
    ]
    if faq:
        graph.append({
            "@type": "FAQPage",
            "@id": f"{url}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faq
            ],
        })

    head = chrome.head_html(
        title=f"{a['title']} — Jesus Says",
        description=a["description"],
        canonical=url,
        og_type="article",
        json_ld=graph,
    )
    related = "\n".join(
        f'        <li><a href="/content/{r}.html"><strong>{chrome.esc(by_slug[r]["label"])}</strong>'
        f'<span>{chrome.esc(by_slug[r]["description"])}</span></a></li>'
        for r in a["related"]
    )
    scripture = "" if a["category"] == "compare" else "<span>Scripture: King James Version</span>"
    campaign = f"content-{a['slug']}"
    return f"""<!doctype html>
<html lang="en">
<head>
{head}
</head>
<body>
{chrome.nav_html(current="library")}

<main id="main">
  <div class="art-page">
    <article>
      <a class="art-back" href="/content/">{BACK_SVG} Faith Library</a>
      <span class="sec-tag">{chrome.esc(a['kind'])}</span>
      <h1>{chrome.esc(a['h1'])}</h1>
      <div class="art-meta">{byline(author)}<span>Updated <time datetime="{a['modified']}">{human_date(a['modified'])}</time></span>{scripture}</div>
      <div class="art-body">
{BODY_START}
{body}
{BODY_END}
      </div>
    </article>

    <aside class="app-cta" aria-labelledby="cta-title">
      <span class="sec-tag">The Jesus Says app</span>
      <h2 id="cta-title">{CTA_HEADINGS[a['category']]}</h2>
      <p>{CTA_BODY}</p>
      {chrome.app_store_button(campaign)}
      <small>{CTA_SMALL}</small>
    </aside>

    <nav class="art-related" aria-labelledby="related-title">
      <h2 id="related-title">{RELATED_HEADINGS[a['category']]}</h2>
      <ul>
{related}
      </ul>
    </nav>

    {still_card()}
  </div>
</main>

{chrome.footer_html()}
{chrome.SCRIPTS}
</body>
</html>
"""


def still_card() -> str:
    return ('<a class="still-card" href="/play/still-waters/">\n'
            '      <img src="/assets/screens/2.0/stillwaters.webp" alt="Still Waters in the Jesus Says app: green, red and blue '
            'ink swirling on pale water" width="120" height="120" loading="lazy" />\n'
            '      <span><strong>Need a quiet minute?</strong><span>Touch still water, watch the ink settle, and rest with '
            'Psalm 46:10 in Still Waters, a free moment from the app you can try in your browser.</span>'
            '<span class="go">Play Still Waters →</span></span>\n    </a>')


# ── library index ────────────────────────────────────────────────────────────
def render_library(catalog: dict) -> str:
    url = f"{SITE}/content/"
    arts = catalog["articles"]
    n = len(arts)
    description = (f"{n} free Scripture-based guides from Jesus Says: Bible verses, prayers, and devotionals for anxiety, "
                   "grief, healing, doubt, forgiveness, and everyday faith.")
    graph = [
        chrome.organization_node(),
        chrome.website_node(),
        {
            "@type": "CollectionPage",
            "@id": url,
            "url": url,
            "name": "Faith Library — Jesus Says",
            "description": description,
            "isPartOf": {"@id": chrome.WEBSITE_ID},
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": n,
                "itemListElement": [
                    {"@type": "ListItem", "position": i, "url": article_url(a["slug"]), "name": a["h1"]}
                    for i, a in enumerate(arts, start=1)
                ],
            },
        },
        chrome.breadcrumb_node([("Home", f"{SITE}/"), ("Faith Library", url)]),
    ]
    head = chrome.head_html(title="Faith Library: Verses, Prayers & Devotionals — Jesus Says",
                            description=description, canonical=url, json_ld=graph)
    jump = "\n".join(f'        <li><a href="#{c["id"]}">{chrome.esc(c["name"])}</a></li>' for c in catalog["categories"])
    sections = []
    for c in catalog["categories"]:
        items = [a for a in arts if a["category"] == c["id"]]
        cards = "\n".join(
            f'        <li><a href="/content/{a["slug"]}.html"><span class="kind">{chrome.esc(a["kind"])}</span>'
            f'<strong>{chrome.esc(a["label"])}</strong><span class="desc">{chrome.esc(a["description"])}</span></a></li>'
            for a in items
        )
        sections.append(f"""    <section class="lib-topic" id="{c['id']}" aria-labelledby="{c['id']}-h">
      <h2 id="{c['id']}-h">{chrome.esc(c['name'])}</h2>
      <p>{chrome.esc(c['intro'])}</p>
      <ul class="lib-cards">
{cards}
      </ul>
    </section>""")
    body_sections = "\n\n".join(sections)
    return f"""<!doctype html>
<html lang="en">
<head>
{head}
</head>
<body>
{chrome.nav_html(current="library")}

<main id="main">
  <div class="lib-page">
    <header class="lib-page-head">
      <span class="sec-tag">Faith Library</span>
      <h1>Bible verses, prayers, and devotionals for what you're walking through.</h1>
      <p>{n} free guides, each built on Scripture quoted from the King James Version, with honest answers to the questions people ask in hard and ordinary seasons. Read them here. When you want a daily rhythm, the Jesus Says app is there.</p>
      <ul class="lib-jump" aria-label="Topics">
{jump}
      </ul>
    </header>

{body_sections}

    {still_card()}

    <section class="app-cta" aria-labelledby="cta-title">
      <span class="sec-tag">The Jesus Says app</span>
      <h2 id="cta-title">Two quiet minutes with God, every day.</h2>
      <p>{CTA_BODY}</p>
      {chrome.app_store_button("library")}
      <small>{CTA_SMALL}</small>
    </section>
  </div>
</main>

{chrome.footer_html()}
{chrome.SCRIPTS}
</body>
</html>
"""


# ── author page ──────────────────────────────────────────────────────────────
def render_author(catalog: dict, author: dict) -> str:
    url = f"{SITE}{chrome.AUTHOR_PATH}"
    arts = catalog["articles"]
    reviewer = reviewer_of(author)
    description = (f"Who writes the {len(arts)} Faith Library guides on jesussays.app, how each guide is drafted, "
                   "checked against the King James text and reviewed, and how to send a correction.")
    graph = [
        chrome.organization_node(),
        chrome.website_node(),
        *([person_node(reviewer)] if reviewer else []),
        {
            "@type": "ProfilePage",
            "@id": url,
            "url": url,
            "name": "The Jesus Says team",
            "description": description,
            "isPartOf": {"@id": chrome.WEBSITE_ID},
            "mainEntity": {"@id": person_node(reviewer)["@id"] if reviewer else chrome.ORG_ID},
        },
        chrome.breadcrumb_node([("Home", f"{SITE}/"), ("Faith Library", f"{SITE}/content/"), ("The Jesus Says team", url)]),
    ]
    head = chrome.head_html(title="The Jesus Says Team: Faith Library Authors — Jesus Says",
                            description=description, canonical=url, og_type="profile", json_ld=graph)
    reviewer_html = ""
    if reviewer:
        role = f", {chrome.esc(reviewer['job_title'])}" if reviewer.get("job_title") else ""
        bio = f"\n  <p>{chrome.esc(reviewer['bio'])}</p>" if reviewer.get("bio") else ""
        links = "".join(f'\n    <li><a href="{chrome.esc(u)}" rel="me">{chrome.esc(u)}</a></li>' for u in reviewer.get("same_as", []))
        links = f"\n  <ul>{links}\n  </ul>" if links else ""
        reviewer_html = f"""
  <h2 id="reviewer">Who reviews the guides</h2>
  <p><strong>{chrome.esc(reviewer['name'].strip())}</strong>{role} reads and approves each guide before it is published or updated.</p>{bio}{links}
"""
    lists = []
    for c in catalog["categories"]:
        items = "\n".join(f'    <li><a href="/content/{a["slug"]}.html">{chrome.esc(a["h1"])}</a></li>'
                          for a in arts if a["category"] == c["id"])
        lists.append(f'  <h3>{chrome.esc(c["name"])}</h3>\n  <ul>\n{items}\n  </ul>')
    guide_lists = "\n".join(lists)
    return f"""<!doctype html>
<html lang="en">
<head>
{head}
</head>
<body>
{chrome.nav_html(current="library")}

<main id="main" class="page author-page">
  <span class="sec-tag">Faith Library authors</span>
  <h1>The Jesus Says team</h1>
  <p>The Jesus Says team makes <strong>Jesus Says: Daily Reflection</strong>, an iPhone and iPad app for a daily practice with Scripture, and writes the {len(arts)} guides in the <a href="/content/">Faith Library</a>. Every guide on this site is credited to the team.</p>
{reviewer_html}
  <h2 id="how-we-write">How the guides are written</h2>
  <ol>
    <li><p><strong>One guide for each real question.</strong> Each guide answers a question people bring to Scripture, such as how to pray when they can&rsquo;t sleep or whether anger is a sin. When a guide already answers a question, we improve that guide instead of adding a near-copy.</p></li>
    <li><p><strong>Drafted with AI writing tools.</strong> Guides are drafted and revised with the help of AI writing tools, working from our written editorial guidelines.</p></li>
    <li><p><strong>Scripture checked word for word.</strong> Before a guide can be published, a script checks every quotation against the King James text bundled in the app. Verses are read in context, and a guide says so when a popular verse is often misapplied.</p></li>
    <li><p><strong>Read and approved by a person.</strong> Nothing in the Faith Library is published automatically. A person on the team reads each new guide or update and approves it before it goes live.</p></li>
    <li><p><strong>Care notes on hard topics.</strong> Guides on depression, grief, anxiety, addiction, illness, and relationships point readers to pastors, counselors, doctors, and crisis lines such as 988.</p></li>
  </ol>
  <p>The full rules are in our <a href="/about.html#editorial">editorial standards</a>.</p>

  <h2 id="guides">Guides by the Jesus Says team</h2>
{guide_lists}

  <h2 id="contact">Corrections and contact</h2>
  <p>If a guide misquotes a verse, uses one out of context, or says something that seems unkind or unsafe, email <a href="mailto:{chrome.CONTACT_EMAIL}">{chrome.CONTACT_EMAIL}</a>. The team also posts on <a href="{chrome.INSTAGRAM_URL}" rel="me">Instagram</a>, <a href="{chrome.X_URL}" rel="me">X</a>, and <a href="{chrome.TIKTOK_URL}" rel="me">TikTok</a>.</p>
</main>

{chrome.footer_html()}
{chrome.SCRIPTS}
</body>
</html>
"""


# ── sitemap, llms.txt, redirects ─────────────────────────────────────────────
STATIC_URLS = [
    ("/", "2026-09-28"),
    ("/content/", "2026-09-29"),
    ("/play/still-waters/", "2026-09-29"),
    ("/download.html", "2026-09-29"),
    ("/about.html", "2026-09-29"),
    ("/author/jesus-says-team/", "2026-09-29"),
    ("/privacy_policy.html", "2026-09-27"),
    ("/terms_of_use.html", "2026-09-27"),
]


def render_sitemap(catalog: dict) -> str:
    rows = [(f"{SITE}{path}", mod) for path, mod in STATIC_URLS]
    rows += [(article_url(a["slug"]), a["modified"]) for a in catalog["articles"]]
    body = "\n".join(f"  <url><loc>{loc}</loc><lastmod>{mod}</lastmod></url>" for loc, mod in rows)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")


def render_llms(catalog: dict) -> str:
    lines = [
        "# Jesus Says",
        "",
        "> Jesus Says: Daily Reflection is an iPhone and iPad app for daily Scripture reflection and prayer. "
        "jesussays.app is its official website and publishes a small library of Scripture-based guides.",
        "",
        "Key facts:",
        f"- App Store: {chrome.APP_STORE_URL}",
        "- Platforms: iPhone and iPad (no Android version).",
        "- Price: free to download with 7 days of full access; Plus Monthly and Plus Annual subscriptions continue it.",
        "- Daily practice: one verse, one reflection, one prayer, and one step for today (\"Today with God\").",
        "- Speak or type a private reflection and receive Scripture, a short reflection, and a prayer.",
        "- Also: a 7-day path through Scripture, Be Still quiet moments (Still Waters, Peace Be Still, Consider the Heavens), "
        "Listen Mode read-aloud, a private Verse Library and journal, and the full King James Bible.",
        "- Responses are generated from Scripture and are not reviewed by religious authorities. The app is not a replacement "
        "for church, pastoral care, counseling, medical care, or emergency services.",
        "- Website Scripture quotations use the King James Version (public domain), matching the app's Bible reader.",
        f"- Contact: {chrome.CONTACT_EMAIL}",
        "",
        "## App",
        f"- [Jesus Says on the App Store]({chrome.APP_STORE_URL}): download page for iPhone and iPad",
        f"- [About the app]({SITE}/download.html): features, screenshots, and pricing",
        f"- [Still Waters]({SITE}/play/still-waters/): a free, quiet ink-on-water moment from the app that runs in the browser",
        f"- [About Jesus Says]({SITE}/about.html): who publishes the site and its editorial standards",
        f"- [The Jesus Says team]({SITE}{chrome.AUTHOR_PATH}): who writes the Faith Library and how guides are drafted, checked and reviewed",
        "",
        "## Faith Library",
    ]
    for c in catalog["categories"]:
        lines += ["", f"### {c['name']}"]
        for a in (x for x in catalog["articles"] if x["category"] == c["id"]):
            lines.append(f"- [{a['h1']}]({article_url(a['slug'])}): {a['description']}")
    lines += [
        "",
        "## Optional",
        f"- [Privacy Policy]({SITE}/privacy_policy.html)",
        f"- [Terms of Use]({SITE}/terms_of_use.html)",
        "",
    ]
    return "\n".join(lines)


def render_stub(target_slug: str, target_title: str) -> str:
    url = article_url(target_slug)
    t = chrome.esc(target_title)
    return f"""<!doctype html>
{STUB_MARK}
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{t} — Jesus Says</title>
<link rel="canonical" href="{url}" />
<meta name="robots" content="noindex, follow" />
<meta http-equiv="refresh" content="0; url=/content/{target_slug}.html" />
</head>
<body>
<p>This page has moved to <a href="/content/{target_slug}.html">{t}</a>.</p>
<script>location.replace("/content/{target_slug}.html" + location.hash)</script>
</body>
</html>
"""


# ── validation ───────────────────────────────────────────────────────────────
def validate(catalog: dict, redirects: dict[str, str], pages: dict[str, str]) -> list[str]:
    problems = []
    slugs = [a["slug"] for a in catalog["articles"]]
    known = set(slugs)
    cats = {c["id"] for c in catalog["categories"]}
    if len(known) != len(slugs):
        problems.append("duplicate slugs in catalog")
    for a in catalog["articles"]:
        if a["category"] not in cats:
            problems.append(f"{a['slug']}: unknown category {a['category']}")
        for r in a["related"]:
            if r not in known or r == a["slug"]:
                problems.append(f"{a['slug']}: bad related slug {r}")
        for key in ("title", "h1", "description", "label", "published", "modified", "kind"):
            if not a.get(key):
                problems.append(f"{a['slug']}: missing {key}")
        if len(a.get("description", "")) > 170:
            problems.append(f"{a['slug']}: description over 170 chars")
    for old, new in redirects.items():
        if old in known:
            problems.append(f"redirect source {old} is also a live article")
        if new not in known:
            problems.append(f"redirect {old} -> {new}: target is not a catalog article")
    for slug, body in pages.items():
        for link in re.findall(r'href="/content/([^"#]+)\.html', body):
            if link not in known:
                problems.append(f"{slug}: links to /content/{link}.html which is not a live article")
    registered = known | set(redirects) | {"index"}
    for path in CONTENT.glob("*.html"):
        if path.stem not in registered:
            problems.append(f"content/{path.name} is not registered in _data/library.json or _data/redirects.json")
    for rel in HAND_PAGES:
        path = ROOT / rel
        if path.exists():
            for link in re.findall(r'href="/content/([^"#]+)\.html', path.read_text(encoding="utf-8")):
                if link not in known:
                    problems.append(f"{rel}: links to /content/{link}.html which is not a live article")
    return problems


# ── main ─────────────────────────────────────────────────────────────────────
def build(ingest: Path | None = None, check: bool = False) -> int:
    """Rebuild everything (or only validate). Returns a process exit code."""
    args = argparse.Namespace(ingest=ingest, check=check)
    catalog = load_catalog()
    author = load_author()
    redirects = json.loads(REDIRECTS.read_text(encoding="utf-8")) if REDIRECTS.exists() else {}

    bodies: dict[str, str] = {}
    for a in catalog["articles"]:
        path = CONTENT / f"{a['slug']}.html"
        if args.ingest and (args.ingest / f"{a['slug']}.html").exists():
            bodies[a["slug"]] = (args.ingest / f"{a['slug']}.html").read_text(encoding="utf-8").strip("\n")
            meta_path = args.ingest / f"{a['slug']}.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                for key, field in (("title", "title"), ("h1", "h1"), ("description", "description"), ("library_label", "label")):
                    if meta.get(key):
                        a[field] = meta[key].strip()
        elif path.exists():
            bodies[a["slug"]] = extract_body(path.read_text(encoding="utf-8"))
        else:
            print(f"ERROR content/{a['slug']}.html missing and no ingested body", file=sys.stderr)
            return 1

    problems = validate(catalog, redirects, bodies)
    if problems:
        print("Build problems:", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        if args.check or not args.ingest:
            return 1
    if args.check:
        print(f"OK  {len(catalog['articles'])} articles, {len(redirects)} redirects")
        return 0

    if args.ingest:
        CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for a in catalog["articles"]:
        (CONTENT / f"{a['slug']}.html").write_text(with_analytics(render_article(a, bodies[a["slug"]], catalog, author)), encoding="utf-8")
    (CONTENT / "index.html").write_text(with_analytics(render_library(catalog)), encoding="utf-8")
    author_page = ROOT / chrome.AUTHOR_PATH.strip("/") / "index.html"
    author_page.parent.mkdir(parents=True, exist_ok=True)
    author_page.write_text(with_analytics(render_author(catalog, author)), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(render_sitemap(catalog), encoding="utf-8")
    (ROOT / "llms.txt").write_text(render_llms(catalog), encoding="utf-8")
    titles = {a["slug"]: a["h1"] for a in catalog["articles"]}
    for old, new in redirects.items():
        (CONTENT / f"{old}.html").write_text(with_analytics(render_stub(new, titles[new])), encoding="utf-8")

    for rel, (home, current) in HAND_PAGES.items():
        path = ROOT / rel
        if not path.exists():
            continue
        page = path.read_text(encoding="utf-8")
        prefix = "still-waters" if rel.startswith("play/") else ""
        page = replace_block(page, "nav", chrome.nav_html(home=home, current=current, campaign_prefix=prefix))
        page = replace_block(page, "footer", chrome.footer_html(home=home, campaign_prefix=prefix))
        if "<!-- site:faq-ld -->" in page:
            page = replace_block(page, "faq-ld", home_faq_ld(page))
        path.write_text(with_analytics(page), encoding="utf-8")

    remaining = validate(catalog, redirects, bodies)
    for p in remaining:
        print(f"  • {p}", file=sys.stderr)
    print(f"Built {len(catalog['articles'])} articles, library index, sitemap, llms.txt, {len(redirects)} redirects.")
    return 1 if remaining else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ingest", type=Path, help="directory with <slug>.html bodies and <slug>.json metadata")
    ap.add_argument("--check", action="store_true", help="validate only")
    args = ap.parse_args()
    return build(args.ingest, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
