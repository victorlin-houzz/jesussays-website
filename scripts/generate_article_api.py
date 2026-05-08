#!/usr/bin/env python3
"""Generate one AEO article from the keyword queue using Anthropic API (for GitHub Actions)."""
import json
import re
import sys
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

import anthropic

client = anthropic.Anthropic()

QUEUE_PATH = Path("content/queue.json")
SITEMAP_PATH = Path("sitemap.xml")
LLMS_PATH = Path("llms.txt")
BASE_URL = "https://victorlin-houzz.github.io/jesussays-website"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

SYSTEM = """You write AEO-optimized HTML pages for Jesus Says, a Christian guidance website.
Output ONLY raw HTML — no markdown fences, no explanation.

Required structure:
<!doctype html><html lang="en"><head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>[Keyword Title] — Jesus Says 2026</title>
  <meta name="description" content="[150-160 char direct-answer]">
  <meta name="keywords" content="[primary keyword], jesus says, bible, prayer, christian">
  <link rel="canonical" href="BASE_URL/content/SLUG.html">
  <link rel="stylesheet" href="/jesussays-website/assets/site.css">
  <script type="application/ld+json">{"@context":"https://schema.org","@graph":[
    {"@type":"Article","headline":"...","description":"...","datePublished":"TODAY","author":{"@type":"Organization","name":"Jesus Says"},"mainEntityOfPage":{"@type":"WebPage","@id":"BASE_URL/content/SLUG.html"}},
    {"@type":"FAQPage","mainEntity":[
      {"@type":"Question","name":"Q1","acceptedAnswer":{"@type":"Answer","text":"A1 40-60 words"}},
      {"@type":"Question","name":"Q2","acceptedAnswer":{"@type":"Answer","text":"A2 40-60 words"}},
      {"@type":"Question","name":"Q3","acceptedAnswer":{"@type":"Answer","text":"A3 40-60 words"}},
      {"@type":"Question","name":"Q4","acceptedAnswer":{"@type":"Answer","text":"A4 40-60 words"}},
      {"@type":"Question","name":"Q5","acceptedAnswer":{"@type":"Answer","text":"A5 40-60 words"}}
    ]},
    {"@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":"BASE_URL/"},
      {"@type":"ListItem","position":2,"name":"...","item":"BASE_URL/content/SLUG.html"}
    ]}
  ]}</script>
</head><body><main class="container">
  <nav><a href="/jesussays-website/">← Home</a></nav>
  <h1>[Title]</h1>
  <p>[Direct answer: 40-60 words, no preamble]</p>
  <h2>[Question H2]</h2>
  <ol><li><strong>Ref</strong> — "verse." Application.</li>[4-6 verses]</ol>
  <h2>[How-to H2]</h2>
  <ol><li>[Step]</li>[3-5 steps]</ol>
  <h2>[Follow-up H2]</h2>
  <p>[40-60 word answer]</p>
  <section class="faq"><h2>Frequently Asked Questions</h2>
    <h3>[Q]</h3><p>[A 40-60 words]</p>
    <h3>[Q]</h3><p>[A 40-60 words]</p>
    <h3>[Q]</h3><p>[A 40-60 words]</p>
    <h3>[Q]</h3><p>[A 40-60 words]</p>
    <h3>[Q]</h3><p>[A 40-60 words]</p>
  </section>
  <section class="app-cta">
    <h2>Get Daily Scripture for Your Exact Moment</h2>
    <p>Jesus Says brings personalized Bible verses, prayer prompts, and confession journaling to your phone.</p>
    <a class="cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&utm_medium=cta&utm_campaign=organic" rel="nofollow">Download Jesus Says — Free</a>
  </section>
</main></body></html>

Tone: warm, theologically sound, non-preachy. 800-1000 words body."""


def load_queue() -> list[dict]:
    return json.loads(QUEUE_PATH.read_text())


def save_queue(queue: list[dict]) -> None:
    QUEUE_PATH.write_text(json.dumps(queue, indent=2) + "\n")


def next_item(queue: list[dict]) -> dict | None:
    return next((q for q in queue if q["status"] == "pending"), None)


def generate_html(keyword: str, slug: str) -> str:
    today = date.today().isoformat()
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": f'Keyword: "{keyword}"\nSlug: {slug}\nDate: {today}'}]
    )
    return response.content[0].text


def update_sitemap(slug: str) -> None:
    ET.register_namespace("", NS)
    tree = ET.parse(SITEMAP_PATH)
    root = tree.getroot()
    url_el = ET.SubElement(root, f"{{{NS}}}url")
    ET.SubElement(url_el, f"{{{NS}}}loc").text = f"{BASE_URL}/content/{slug}.html"
    ET.SubElement(url_el, f"{{{NS}}}lastmod").text = date.today().isoformat()
    ET.SubElement(url_el, f"{{{NS}}}changefreq").text = "monthly"
    ET.SubElement(url_el, f"{{{NS}}}priority").text = "0.8"
    ET.indent(tree, space="  ")
    tree.write(SITEMAP_PATH, encoding="unicode", xml_declaration=True)


def update_llms(keyword: str, slug: str) -> None:
    text = LLMS_PATH.read_text()
    new_line = f"- /content/{slug}.html — {keyword.capitalize()}"
    if f"/content/{slug}.html" not in text:
        marker = "## Primary Intent Coverage"
        text = text.replace(marker, f"{new_line}\n{marker}")
        LLMS_PATH.write_text(text)


def main() -> None:
    queue = load_queue()
    item = next_item(queue)
    if item is None:
        print("Queue exhausted.")
        sys.exit(0)

    keyword = item["keyword"]
    slug = item["slug"]
    out_path = Path("content") / f"{slug}.html"

    if out_path.exists():
        print(f"Already exists: {out_path} — skipping.")
        for q in queue:
            if q["keyword"] == keyword:
                q["status"] = "published"
        save_queue(queue)
        sys.exit(0)

    print(f"Generating: {keyword}")
    html = generate_html(keyword, slug)
    out_path.write_text(html, encoding="utf-8")
    print(f"Written: {out_path}")

    update_sitemap(slug)
    update_llms(keyword, slug)

    for q in queue:
        if q["keyword"] == keyword:
            q["status"] = "published"
            q["published_date"] = date.today().isoformat()
    save_queue(queue)
    print("Done.")


if __name__ == "__main__":
    main()
