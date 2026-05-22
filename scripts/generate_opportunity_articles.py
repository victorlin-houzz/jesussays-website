#!/usr/bin/env python3
"""Generate a batch of original Jesus Says articles from opportunities."""
from __future__ import annotations

import argparse
import html as html_lib
import json
import subprocess
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from generate_article import AEO_TEMPLATE, BASE_URL, LLMS_PATH, NS, SITEMAP_PATH
from manage_opportunities import (
    OPPORTUNITIES_PATH,
    load_opportunities,
    normalized_topic_slug,
    write_opportunities,
)

CONTENT_DIR = Path("content")
LIBRARY_PATH = CONTENT_DIR / "index.html"

SCRIPTURE_SETS = {
    "anxiety": [
        ("Philippians 4:6-7", "Bring anxious thoughts to God in prayer, with thanksgiving, and receive his guarding peace."),
        ("1 Peter 5:7", "Cast anxiety on God because his care is personal, not distant."),
        ("Matthew 6:34", "Receive today's grace instead of carrying tomorrow before it arrives."),
        ("Psalm 94:19", "When cares multiply inside, God's comfort can steady the soul."),
        ("John 14:27", "Jesus gives a peace deeper than the world can manufacture."),
    ],
    "healing": [
        ("Psalm 147:3", "God is near to the brokenhearted and attentive to wounds that are seen and unseen."),
        ("James 5:14-15", "Christian healing belongs with prayer, community, and humble trust in God's mercy."),
        ("Isaiah 40:29", "God gives strength to the weary when their own strength is gone."),
        ("Jeremiah 17:14", "A prayer for healing can be honest, simple, and directed to the Lord."),
        ("2 Corinthians 12:9", "God's grace can be sufficient even while weakness remains."),
    ],
    "depression": [
        ("Psalm 34:18", "The Lord is near to the brokenhearted and does not despise a crushed spirit."),
        ("Lamentations 3:22-23", "God's mercy can meet a person again in the morning."),
        ("Matthew 11:28", "Jesus invites the weary to come to him for rest."),
        ("Romans 8:38-39", "Nothing can separate believers from the love of God in Christ."),
        ("Psalm 42:11", "The soul can speak hope to itself while still waiting for light."),
    ],
    "love": [
        ("1 Corinthians 13:4-7", "Biblical love is patient, kind, truthful, and enduring."),
        ("1 John 4:19", "We learn to love because God first loved us."),
        ("John 13:34-35", "Jesus calls his people to love one another as a sign of discipleship."),
        ("Romans 12:10", "Love honors others with warmth, humility, and devotion."),
        ("Colossians 3:14", "Love binds Christian virtues together in maturity."),
    ],
    "fear": [
        ("Isaiah 41:10", "God tells his people not to fear because he is with them and will strengthen them."),
        ("Psalm 56:3", "Fear can become a prompt to trust God in the moment it rises."),
        ("2 Timothy 1:7", "God gives a spirit marked by power, love, and self-control."),
        ("Joshua 1:9", "Courage grows from God's presence, not from pretending danger is unreal."),
        ("Psalm 23:4", "Even in dark valleys, God's nearness comforts and guides."),
    ],
}

SENSITIVE_WORDS = {"anxiety", "depression", "healing", "fear"}


def content_slugs() -> set[str]:
    return {
        p.stem
        for p in CONTENT_DIR.glob("*.html")
        if p.stem not in {"index", "keyword-clusters"}
    }


def queued_or_existing_normalized(rows: list[dict]) -> set[str]:
    slugs = content_slugs()
    slugs |= {
        row["target_slug"]
        for row in rows
        if row["status"] in {"queued", "drafted", "published"}
    }
    return {normalized_topic_slug(slug) for slug in slugs}


def generate_html(row: dict, local_only: bool = False) -> str:
    if local_only:
        return render_local_html(row)
    today = date.today().isoformat()
    prompt = AEO_TEMPLATE.substitute(
        keyword=row["primary_keyword"],
        slug=row["target_slug"],
        today=today,
        base_url=BASE_URL,
    )
    prompt += f"""

Opportunity metadata for originality and conversion:
- Source site: {row['source_site']}
- Source URL: {row['source_url']}
- Source title: {row['source_title']}
- Detected user intent: {row['detected_intent']}
- Original Jesus Says title to use: {row['jesus_says_title']}
- User need: {row['user_need']}
- Jesus Says angle: {row['jesus_says_angle']}
- App CTA angle: {row['app_cta_angle']}

Originality rules:
- Treat the source URL as a demand signal only. Do not copy competitor wording, outline, order, or proprietary devotional material.
- Write an original Jesus Says article tailored to personalized Scripture, voice prayer, confession journaling, and daily devotional app use.
- If the topic touches anxiety, depression, addiction, self-harm, medical care, grief, surgery, cancer, trauma, or hopelessness, include a compassionate care note saying Scripture and prayer support care but do not replace professional, pastoral, medical, emergency, or crisis help.
- Keep claims humble. Do not promise healing, cures, guaranteed financial outcomes, or that app usage will fix a mental health or medical condition.
- Make the final app CTA specific to this topic and keep the App Store link UTM campaign as content-{row['target_slug']}.

Output rules:
- Return only the complete HTML document. Do not describe what you wrote.
- Start with <!doctype html> and end with </html>.
- Escape quotes correctly inside JSON-LD so every application/ld+json script parses as valid JSON.
- Keep visible article copy between 750 and 1,500 words. Do not include template placeholders such as TODAY or KEYWORD.
"""
    result = subprocess.run(
        ["claude", "-p", prompt, "--allowedTools", ""],
        capture_output=True,
        text=True,
        timeout=240,
    )
    if result.returncode != 0:
        return render_local_html(row)
    html = result.stdout.strip()
    if not html.lower().startswith("<!doctype html") or "</html>" not in html.lower():
        return render_local_html(row)
    return html


def topic_key(row: dict) -> str:
    haystack = " ".join([row["target_slug"], row["primary_keyword"], row["jesus_says_title"]]).lower()
    for key in SCRIPTURE_SETS:
        if key in haystack:
            return key
    return "anxiety"


def title_text(row: dict) -> str:
    return row["jesus_says_title"].strip()


def category_label(row: dict) -> str:
    return row.get("content_type") or "Christian Advice"


def render_local_html(row: dict) -> str:
    """Deterministic fallback when the content model is unavailable or malformed."""
    today = date.today().isoformat()
    slug = row["target_slug"]
    topic = topic_key(row)
    title = title_text(row)
    keyword = row["primary_keyword"]
    verses = SCRIPTURE_SETS[topic]
    desc = f"{title} with Scripture, prayer, practical reflection, and a gentle Jesus Says app prompt for daily faith."
    if len(desc) > 158:
        desc = desc[:155].rsplit(" ", 1)[0] + "..."
    direct = f"{title} begins by bringing {html_lib.escape(keyword)} to God honestly, then anchoring the heart in Scripture, prayer, and one small faithful next step."
    care_note = ""
    if topic in SENSITIVE_WORDS:
        care_note = """
    <div class="care-note">
      <p><strong>Care note:</strong> Scripture and prayer can support your heart, but they do not replace professional, pastoral, medical, emergency, or crisis help. If you feel unsafe or overwhelmed, contact local emergency services, a trusted pastor or counselor, or the 988 Suicide &amp; Crisis Lifeline in the United States.</p>
    </div>"""
    verse_items = "\n".join(
        f"      <li><strong>{ref}</strong> — {html_lib.escape(application)}</li>" for ref, application in verses
    )
    steps = [
        f"Name the concern plainly before God instead of editing it into religious language.",
        f"Read one passage slowly and ask what it reveals about God's presence, character, or invitation.",
        "Turn the passage into a one-sentence prayer you can repeat during the day.",
        "Write one confession or release statement, especially if fear, resentment, or control is shaping your response.",
        "Choose one concrete act of obedience: ask for help, rest, apologize, encourage someone, or return to the verse tonight.",
    ]
    step_items = "\n".join(f"      <li>{html_lib.escape(step)}</li>" for step in steps)
    faqs = [
        (f"What is the best way to start {keyword}?", f"Start with one honest sentence to God, then read a short passage connected to {keyword}. A small practice done sincerely is better than a long practice performed under pressure."),
        (f"Can the Bible help with {keyword}?", f"The Bible helps by revealing God's character, naming human struggle honestly, and giving language for prayer. It should be received as spiritual support, not as a denial of wise counsel or practical care."),
        ("How can I pray when I do not have words?", "Use a simple pattern: Lord, here is what I feel; here is what I need; here is what I release; here is one step I will take with you today."),
        ("Why use the Jesus Says app with this topic?", "Jesus Says can turn a broad concern into a daily rhythm of Scripture, prayer prompts, and confession journaling that fits the exact moment you are facing."),
        ("How often should I return to this practice?", "Return daily for a week, even if only for five minutes. Repetition helps Scripture move from a page you read into a truth you remember under pressure."),
    ]
    faq_html = "\n".join(f"      <h3>{html_lib.escape(q)}</h3><p>{html_lib.escape(a)}</p>" for q, a in faqs)
    faq_schema = [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in faqs
    ]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "@id": f"{BASE_URL}/#organization", "name": "Jesus Says", "url": f"{BASE_URL}/", "logo": f"{BASE_URL}/assets/og-image.png"},
            {"@type": "Article", "headline": title, "description": desc, "datePublished": today, "dateModified": today, "author": {"@id": f"{BASE_URL}/#organization"}, "publisher": {"@id": f"{BASE_URL}/#organization"}, "image": f"{BASE_URL}/assets/og-image.png", "mainEntityOfPage": {"@type": "WebPage", "@id": f"{BASE_URL}/content/{slug}.html"}},
            {"@type": "FAQPage", "mainEntity": faq_schema},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Faith Library", "item": f"{BASE_URL}/content/"},
                {"@type": "ListItem", "position": 3, "name": title, "item": f"{BASE_URL}/content/{slug}.html"},
            ]},
        ],
    }
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html_lib.escape(title)} — Jesus Says</title>
  <meta name="description" content="{html_lib.escape(desc)}" />
  <meta name="keywords" content="{html_lib.escape(keyword)}, jesus says, bible, prayer, christian" />
  <link rel="canonical" href="{BASE_URL}/content/{slug}.html" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:title" content="{html_lib.escape(title)} — Jesus Says" />
  <meta property="og:description" content="{html_lib.escape(desc)}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{BASE_URL}/content/{slug}.html" />
  <meta property="og:image" content="{BASE_URL}/assets/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html_lib.escape(title)} — Jesus Says" />
  <meta name="twitter:description" content="{html_lib.escape(desc)}" />
  <meta name="twitter:image" content="{BASE_URL}/assets/og-image.png" />
  <link rel="stylesheet" href="/assets/landing.css" />
  <script type="application/ld+json">
  {json.dumps(schema, ensure_ascii=False, indent=2)}
  </script>
</head>
<body>
<main>
  <div class="art-page">
    <a class="art-back" href="/content/">Faith Library</a>
    <span class="sec-tag">{html_lib.escape(category_label(row))}</span>
    <h1>{html_lib.escape(title)}</h1>
    <p>{direct}</p>
    <h2>Scripture to carry into this moment</h2>
    <ol>
{verse_items}
    </ol>
    <h2>How to pray through this today</h2>
    <ol>
{step_items}
    </ol>{care_note}
    <h2>A simple prayer</h2>
    <p>Lord Jesus, meet me in this exact place. Let your Word become steady ground beneath my thoughts, my choices, and my desires. Teach me to receive your care without pretending everything is easy, and guide me toward the next faithful step.</p>
    <h2>A short reflection for the rest of the day</h2>
    <p>Most people do not need more religious pressure when they search for {html_lib.escape(keyword)}. They need a way to slow down, tell the truth, and remember that God is not impatient with human weakness. Let this page be a beginning rather than a burden. Choose one verse from above, write it somewhere visible, and return to it before you react, decide, or spiral. The goal is not to feel instantly different. The goal is to practice turning toward God while the situation is still unfinished.</p>
    <p>If another person is involved, ask the Holy Spirit for both courage and gentleness. If the struggle is mostly internal, ask for light without shame. Christian growth often looks like one repeated surrender: this thought, this fear, this longing, this next step. Jesus meets people in ordinary places, and a small faithful practice can become a doorway back to peace.</p>
    <p>Before you leave, decide when you will return to the practice. A verse remembered tonight can become the first thing you reach for tomorrow morning. That simple repetition helps this article become a habit rather than another tab you close.</p>
    <h2>How Jesus Says can support this practice</h2>
    <p>Jesus Says is built for moments when you need Scripture that feels close to real life. Use personalized Bible verses, voice prayer, and confession journaling to turn this topic into a daily rhythm instead of a one-time search.</p>
    <section class="faq">
      <h2>Frequently Asked Questions</h2>
{faq_html}
    </section>
    <section class="app-cta">
      <h2>Get Daily Scripture for Your Exact Moment</h2>
      <p>{html_lib.escape(row['app_cta_angle'])}</p>
      <a class="btn-apple" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=content-{slug}" rel="nofollow">Download on the App Store</a>
    </section>
  </div>
</main>
</body>
</html>
"""


def update_sitemap(slug: str) -> None:
    ET.register_namespace("", NS)
    tree = ET.parse(SITEMAP_PATH)
    root = tree.getroot()
    loc = f"{BASE_URL}/content/{slug}.html"
    ns = {"s": NS}
    existing = {el.text for el in root.findall("s:url/s:loc", ns)}
    if loc in existing:
        return
    url_el = ET.SubElement(root, f"{{{NS}}}url")
    ET.SubElement(url_el, f"{{{NS}}}loc").text = loc
    ET.SubElement(url_el, f"{{{NS}}}lastmod").text = date.today().isoformat()
    ET.SubElement(url_el, f"{{{NS}}}changefreq").text = "monthly"
    ET.SubElement(url_el, f"{{{NS}}}priority").text = "0.8"
    ET.indent(tree, space="  ")
    tree.write(SITEMAP_PATH, encoding="unicode", xml_declaration=True)


def update_llms(row: dict) -> None:
    text = LLMS_PATH.read_text(encoding="utf-8")
    slug = row["target_slug"]
    if f"/content/{slug}.html" in text:
        return
    new_line = f"- /content/{slug}.html — {row['jesus_says_title']}"
    marker = "## Primary Intent Coverage"
    text = text.replace(marker, f"{new_line}\n{marker}")
    LLMS_PATH.write_text(text, encoding="utf-8")


def library_section_id(content_type: str) -> str:
    if content_type == "Prayer":
        return "lib-prayer"
    if content_type == "Devotional":
        return "lib-devotion"
    if content_type == "Confession":
        return "lib-confession"
    if content_type in {"Christian Advice", "AEO Question", "FAQ"}:
        return "lib-advice"
    return "lib-bible"


def update_library(row: dict) -> None:
    text = LIBRARY_PATH.read_text(encoding="utf-8")
    slug = row["target_slug"]
    href = f"/content/{slug}.html"
    if href in text:
        return
    section_id = library_section_id(row["content_type"])
    pattern = f'<section class="lib-section" aria-labelledby="{section_id}">'
    start = text.find(pattern)
    if start == -1:
        raise RuntimeError(f"Could not find library section {section_id}")
    ul_start = text.find("<ul>", start)
    ul_end = text.find("</ul>", ul_start)
    item = f'          <li><a href="{href}">{html_lib.escape(row["jesus_says_title"])}</a></li>\n'
    text = text[:ul_end] + item + text[ul_end:]
    LIBRARY_PATH.write_text(text, encoding="utf-8")


def choose_rows(rows: list[dict], limit: int, ids: list[str]) -> list[dict]:
    if ids:
        wanted = set(ids)
        return [row for row in rows if row["id"] in wanted or row["target_slug"] in wanted]
    blocked = queued_or_existing_normalized(rows)
    candidates = [
        row
        for row in rows
        if row["status"] == "discovered"
        and row["target_slug"] not in content_slugs()
        and normalized_topic_slug(row["target_slug"]) not in blocked
    ]
    candidates.sort(key=lambda row: (-row["priority"], row["id"]))
    return candidates[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--id", action="append", default=[], help="specific opportunity id or slug to generate")
    parser.add_argument("--force", action="store_true", help="overwrite existing generated article files")
    parser.add_argument("--local-only", action="store_true", help="use deterministic local renderer instead of the Claude CLI")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_opportunities(OPPORTUNITIES_PATH)
    selected = choose_rows(rows, args.limit, args.id)
    if not selected:
        print("No eligible opportunities found.")
        return 0

    print(f"Selected {len(selected)} opportunities:")
    for row in selected:
        print(f"  {row['id']} P{row['priority']} {row['target_slug']} — {row['primary_keyword']}")
    if args.dry_run:
        return 0

    for row in selected:
        out_path = CONTENT_DIR / f"{row['target_slug']}.html"
        if out_path.exists() and not args.force:
            row["status"] = "skipped"
            row["notes"] = (row.get("notes") or "") + " Skipped during generation because output file already exists."
            write_opportunities(rows, OPPORTUNITIES_PATH)
            continue
        print(f"Generating {row['id']}: {row['primary_keyword']}", flush=True)
        article_html = generate_html(row, local_only=args.local_only)
        out_path.write_text(article_html, encoding="utf-8")
        update_sitemap(row["target_slug"])
        update_llms(row)
        update_library(row)
        row["status"] = "drafted"
        row["notes"] = (row.get("notes") or "") + f" Drafted on {date.today().isoformat()}."
        write_opportunities(rows, OPPORTUNITIES_PATH)

    write_opportunities(rows, OPPORTUNITIES_PATH)
    print("Batch generation complete. Run audits before marking as published.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
