#!/usr/bin/env python3
"""Generate one AEO article from the keyword queue using the claude CLI."""
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from string import Template
from xml.etree import ElementTree as ET

QUEUE_PATH = Path("content/queue.json")
SITEMAP_PATH = Path("sitemap.xml")
LLMS_PATH = Path("llms.txt")
BASE_URL = "https://jesussays.app"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

# Uses string.Template ($var syntax) so CSS/JS/JSON braces need no escaping.
AEO_TEMPLATE = Template(r"""Write a full AEO-optimized HTML article for the Jesus Says Christian guidance website.

Output ONLY raw HTML — no markdown fences, no explanation.

Follow this EXACT structure (replace ALL [...] placeholders with real content):

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>[Keyword Title] — Jesus Says</title>
  <meta name="description" content="[150-160 char direct-answer description]" />
  <meta name="keywords" content="[primary keyword], jesus says, bible, prayer, christian" />
  <link rel="canonical" href="$base_url/content/$slug.html" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:title" content="[Title] — Jesus Says" />
  <meta property="og:description" content="[description]" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="$base_url/content/$slug.html" />
  <link rel="stylesheet" href="/assets/landing.css" />
  <style>
    .art-page { max-width: 680px; margin: 80px auto 110px; padding: 0 28px; }
    .art-back {
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 13.5px; font-weight: 600; color: var(--ink-soft);
      margin-bottom: 36px; padding: 8px 14px; border-radius: 999px;
      background: rgba(26,31,74,0.05); transition: background .15s, color .15s;
    }
    .art-back:hover { background: rgba(26,31,74,0.10); color: var(--ink); }
    .art-page h1 {
      font-family: var(--serif); font-weight: 700;
      font-size: clamp(28px, 3.5vw, 42px); line-height: 1.1;
      letter-spacing: -0.5px; color: var(--ink);
      margin: 14px 0 20px; text-wrap: balance;
    }
    .art-page h2 {
      font-family: var(--serif); font-weight: 700;
      font-size: 20px; color: var(--ink); margin: 2.5rem 0 0.75rem;
    }
    .art-page h3 {
      font-family: var(--sans); font-weight: 700;
      font-size: 16px; color: var(--ink); margin: 1.5rem 0 0.4rem;
    }
    .art-page p {
      font-family: var(--serif); font-size: 17px;
      line-height: 1.8; color: var(--ink-soft); margin-bottom: 1.1rem;
    }
    .art-page ul, .art-page ol {
      font-family: var(--serif); font-size: 17px; line-height: 1.75;
      color: var(--ink-soft); padding-left: 1.5rem; margin-bottom: 1.1rem;
    }
    .art-page li { margin-bottom: 0.6rem; }
    .art-page strong { color: var(--ink); }
    .art-page .faq {
      background: var(--paper); border: 1px solid var(--line);
      border-radius: var(--r-lg); padding: 32px; margin: 2.5rem 0;
    }
    .art-page .faq h2 { margin-top: 0; }
    .art-page .app-cta {
      background: var(--night); border-radius: var(--r-xl);
      padding: 44px 36px; text-align: center; margin: 2.5rem 0;
      position: relative; overflow: hidden;
    }
    .art-page .app-cta::before {
      content: ''; position: absolute; inset: 0;
      background: radial-gradient(ellipse at 50% 0%, rgba(232,155,44,0.18), transparent 60%);
    }
    .art-page .app-cta > * { position: relative; }
    .art-page .app-cta h2 {
      font-family: var(--serif); font-weight: 700;
      font-size: clamp(20px, 2.5vw, 28px); color: #fff; margin: 0 0 10px;
    }
    .art-page .app-cta p {
      font-family: var(--sans); font-size: 15px;
      color: rgba(246,241,228,0.75); margin: 0 auto 24px;
    }
    @media (max-width: 560px) {
      .art-page { margin-top: 48px; padding: 0 20px; }
      .art-page .faq { padding: 22px 18px; }
      .art-page .app-cta { padding: 32px 22px; }
    }
  </style>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {"@type": "Article", "headline": "[title]", "description": "[description]", "datePublished": "$today", "author": {"@type": "Organization", "name": "Jesus Says"}, "mainEntityOfPage": {"@type": "WebPage", "@id": "$base_url/content/$slug.html"}},
      {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "[Q1]", "acceptedAnswer": {"@type": "Answer", "text": "[A1 40-60 words]"}},
        {"@type": "Question", "name": "[Q2]", "acceptedAnswer": {"@type": "Answer", "text": "[A2 40-60 words]"}},
        {"@type": "Question", "name": "[Q3]", "acceptedAnswer": {"@type": "Answer", "text": "[A3 40-60 words]"}},
        {"@type": "Question", "name": "[Q4]", "acceptedAnswer": {"@type": "Answer", "text": "[A4 40-60 words]"}},
        {"@type": "Question", "name": "[Q5]", "acceptedAnswer": {"@type": "Answer", "text": "[A5 40-60 words]"}}
      ]},
      {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "$base_url/"},
        {"@type": "ListItem", "position": 2, "name": "Faith Library", "item": "$base_url/content/"},
        {"@type": "ListItem", "position": 3, "name": "[title]", "item": "$base_url/content/$slug.html"}
      ]}
    ]
  }
  </script>
</head>
<body>

<!-- Mobile menu overlay -->
<div class="mobile-menu" id="mobile-menu" role="dialog" aria-modal="true" aria-label="Navigation menu" hidden>
  <a href="/">Home</a>
  <a href="/#features">Features</a>
  <a href="/content/">Faith Library</a>
  <a href="/#faq">FAQ</a>
  <a class="mm-cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=article-menu" rel="nofollow">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.08l.01-.01zM12 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
    Get the App
  </a>
</div>

<!-- NAV -->
<div class="nav-wrap">
  <nav class="nav" aria-label="Primary">
    <a href="/" class="brand" aria-label="Jesus Says — Home">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 22V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C9 11 7 9 7 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C15 11 17 9 17 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </span>
      <span class="brand-name">Jesus Says</span>
    </a>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/#features">Features</a>
      <a href="/content/">Faith Library</a>
      <a href="/#faq">FAQ</a>
    </div>
    <a class="nav-cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=article-nav" rel="nofollow">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.08l.01-.01zM12 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
      Get the App
    </a>
    <button class="nav-burger" id="nav-burger" aria-label="Open navigation menu" aria-expanded="false" aria-controls="mobile-menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
  </nav>
</div>

<main>
  <div class="art-page">

    <a class="art-back" href="/content/">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
      Faith Library
    </a>

    <span class="sec-tag">[Category: Bible Verses | Prayer | Devotional | Confession | Christian Advice]</span>
    <h1>[Title]</h1>
    <p>[Intro paragraph: 35-75 words. First sentence directly answers the article's core question; if that is not possible, write a TLDR instead. Warm, clear, Christian, non-preachy.]</p>

    <h2>[Primary question H2]</h2>
    <ol>
      <li><strong>Book Chapter:Verse</strong> — "verse text." One-sentence application.</li>
      [4-6 verses total]
    </ol>

    <h2>[How-to or practical H2]</h2>
    <ol><li>[Step]</li>[3-5 steps]</ol>

    <h2>[Follow-up question H2]</h2>
    <p>[40-60 word answer]</p>

    <section class="faq">
      <h2>Frequently Asked Questions</h2>
      <h3>[Q1]</h3><p>[A1, 40-60 words]</p>
      <h3>[Q2]</h3><p>[A2, 40-60 words]</p>
      <h3>[Q3]</h3><p>[A3, 40-60 words]</p>
      <h3>[Q4]</h3><p>[A4, 40-60 words]</p>
      <h3>[Q5]</h3><p>[A5, 40-60 words]</p>
    </section>

    <section class="app-cta">
      <h2>Get Daily Scripture for Your Exact Moment</h2>
      <p>Jesus Says brings personalized Bible verses, prayer prompts, and confession journaling to your phone.</p>
      <a class="btn-apple" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=content-$slug" rel="nofollow" style="background:var(--gold);color:var(--ink);display:inline-flex;">
        <svg class="apple" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.08l.01-.01zM12 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
        <span class="stack"><small>Download on the</small><span>App Store</span></span>
      </a>
    </section>

  </div>
</main>

<footer class="site">
  <div>
    <div class="brand" style="margin-bottom: 14px;">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 22V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C9 11 7 9 7 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C15 11 17 9 17 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </span>
      <span class="brand-name">Jesus Says</span>
    </div>
    <p class="meta">A daily companion for prayer, reflection, and scripture. A companion, not a replacement for church or pastoral care.</p>
  </div>
  <div>
    <h5>App</h5>
    <ul>
      <li><a href="/#features">Features</a></li>
      <li><a href="/#day">Daily Practice</a></li>
      <li><a href="/#screens">App Tour</a></li>
      <li><a href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=article-footer" rel="nofollow">Download</a></li>
    </ul>
  </div>
  <div>
    <h5>Library</h5>
    <ul>
      <li><a href="/content/bible-verses-anxiety.html">Verses for anxiety</a></li>
      <li><a href="/content/prayer-for-healing.html">Prayer for healing</a></li>
      <li><a href="/content/daily-devotional-today.html">Today's devotional</a></li>
      <li><a href="/content/index.html">All articles</a></li>
    </ul>
  </div>
  <div>
    <h5>Company</h5>
    <ul>
      <li><a href="/#faq">FAQ</a></li>
      <li><a href="mailto:hello@jesussays.app">Contact</a></li>
      <li><a href="/download.html">About the App</a></li>
    </ul>
  </div>
  <div class="legal">
    <span>© 2026 Jesus Says</span>
    <span class="links">
      <a href="mailto:hello@jesussays.app">hello@jesussays.app</a>
    </span>
  </div>
</footer>

<script>
(function() {
  var burger = document.getElementById('nav-burger');
  var menu   = document.getElementById('mobile-menu');
  var isOpen = false;
  function openMenu() {
    isOpen = true;
    menu.removeAttribute('hidden');
    menu.offsetHeight;
    menu.classList.add('open');
    burger.setAttribute('aria-expanded', 'true');
    burger.setAttribute('aria-label', 'Close navigation menu');
    document.body.classList.add('menu-open');
    burger.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>';
    var f = menu.querySelector('a'); if (f) f.focus();
  }
  function closeMenu() {
    isOpen = false;
    menu.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'Open navigation menu');
    document.body.classList.remove('menu-open');
    burger.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';
    setTimeout(function() { if (!isOpen) menu.setAttribute('hidden', ''); }, 300);
    burger.focus();
  }
  burger.addEventListener('click', function() { isOpen ? closeMenu() : openMenu(); });
  document.addEventListener('keydown', function(e) { if (e.key === 'Escape' && isOpen) closeMenu(); });
  menu.querySelectorAll('a').forEach(function(a) {
    a.addEventListener('click', function() { if (isOpen) closeMenu(); });
  });
  document.addEventListener('keydown', function(e) {
    if (!isOpen || e.key !== 'Tab') return;
    var focusable = menu.querySelectorAll('a, button');
    var first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey) { if (document.activeElement === first) { e.preventDefault(); last.focus(); } }
    else { if (document.activeElement === last) { e.preventDefault(); first.focus(); } }
  });
})();
</script>
</body>
</html>

Keyword: "$keyword"
Slug: $slug
Date: $today
Tone: warm, theologically sound, non-preachy. 800-1000 words body content (between h1 and the FAQ section).
The first paragraph immediately below <h1> must follow this prompt exactly in spirit: "Write me an intro for this piece of content that answers the question in the first sentence. If not possible write me a tldr."
Make that intro a single 35-75 word paragraph whose first sentence directly answers the core question when possible; otherwise write a TLDR.
Replace ALL [...] placeholders with actual content. Output ONLY the HTML.""")


def load_queue() -> list[dict]:
    return json.loads(QUEUE_PATH.read_text())


def save_queue(queue: list[dict]) -> None:
    QUEUE_PATH.write_text(json.dumps(queue, indent=2) + "\n")


def next_item(queue: list[dict]) -> dict | None:
    return next((q for q in queue if q["status"] == "pending"), None)


def generate_html(keyword: str, slug: str) -> str:
    today = date.today().isoformat()
    prompt = AEO_TEMPLATE.substitute(
        keyword=keyword, slug=slug, today=today, base_url=BASE_URL
    )
    result = subprocess.run(
        ["claude", "-p", prompt, "--allowedTools", ""],
        capture_output=True, text=True, timeout=180
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr[:500]}")
    return result.stdout.strip()


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
        print("Queue exhausted — nothing to publish.")
        sys.exit(0)

    keyword = item["keyword"]
    slug = item["slug"]
    out_path = Path("content") / f"{slug}.html"

    if out_path.exists():
        print(f"Already exists: {out_path} — marking published and skipping.")
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
    print("Sitemap updated.")

    update_llms(keyword, slug)
    print("llms.txt updated.")

    for q in queue:
        if q["keyword"] == keyword:
            q["status"] = "published"
            q["published_date"] = date.today().isoformat()
    save_queue(queue)
    print("Queue updated.")


if __name__ == "__main__":
    main()
