#!/usr/bin/env python3
"""Rewrite existing content pages to AEO format using Claude API."""
import anthropic
import sys
from pathlib import Path

client = anthropic.Anthropic()

SYSTEM = """You rewrite Christian HTML content pages to AEO (Answer Engine Optimization) format.

Output ONLY valid raw HTML — no markdown fences, no explanation, no comments outside HTML.

Required structure:
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>[Primary Keyword]: [N] [Type] — Jesus Says 2026</title>
  <meta name="description" content="[150-160 char direct-answer description]">
  <meta name="keywords" content="[primary keyword], jesus says, bible, prayer, christian">
  <link rel="canonical" href="https://victorlin-houzz.github.io/jesussays-website/content/[SLUG].html">
  <link rel="stylesheet" href="/jesussays-website/assets/site.css">
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Article",
        "headline": "...",
        "description": "...",
        "author": {"@type": "Organization", "name": "Jesus Says"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": "https://victorlin-houzz.github.io/jesussays-website/content/[SLUG].html"}
      },
      {
        "@type": "FAQPage",
        "mainEntity": [
          {"@type": "Question", "name": "Q1", "acceptedAnswer": {"@type": "Answer", "text": "A1 (40-60 words)"}},
          {"@type": "Question", "name": "Q2", "acceptedAnswer": {"@type": "Answer", "text": "A2 (40-60 words)"}},
          {"@type": "Question", "name": "Q3", "acceptedAnswer": {"@type": "Answer", "text": "A3 (40-60 words)"}},
          {"@type": "Question", "name": "Q4", "acceptedAnswer": {"@type": "Answer", "text": "A4 (40-60 words)"}},
          {"@type": "Question", "name": "Q5", "acceptedAnswer": {"@type": "Answer", "text": "A5 (40-60 words)"}}
        ]
      },
      {
        "@type": "BreadcrumbList",
        "itemListElement": [
          {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://victorlin-houzz.github.io/jesussays-website/"},
          {"@type": "ListItem", "position": 2, "name": "[Title]", "item": "https://victorlin-houzz.github.io/jesussays-website/content/[SLUG].html"}
        ]
      }
    ]
  }
  </script>
</head>
<body>
<main class="container">
  <p><a href="/jesussays-website/">← Home</a></p>
  <h1>[Title matching the primary keyword intent]</h1>
  <p>[Direct answer: 40-60 words, no preamble, answers the core question immediately]</p>
  <h2>[Primary sub-question phrased as a user question, e.g. "What does the Bible say about X?"]</h2>
  <ol>
    <li><strong>Book Chapter:Verse</strong> — "verse text." One-sentence practical application.</li>
    [4-6 verses]
  </ol>
  <h2>[How-to or practical question, e.g. "How to pray when X" or "What to do when X"]</h2>
  <ol>
    <li>[Specific actionable step]</li>
    [3-5 steps]
  </ol>
  <h2>[Follow-up question specific to this topic]</h2>
  <p>[40-60 word atomic answer]</p>
  <section class="faq">
    <h2>Frequently Asked Questions</h2>
    <h3>[Question 1]</h3><p>[40-60 word answer]</p>
    <h3>[Question 2]</h3><p>[40-60 word answer]</p>
    <h3>[Question 3]</h3><p>[40-60 word answer]</p>
    <h3>[Question 4]</h3><p>[40-60 word answer]</p>
    <h3>[Question 5]</h3><p>[40-60 word answer]</p>
  </section>
  <section class="app-cta">
    <h2>Get Daily Scripture for Your Exact Moment</h2>
    <p>Jesus Says brings personalized Bible verses, prayer prompts, and confession journaling to your phone.</p>
    <a class="cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&utm_medium=cta&utm_campaign=organic" rel="nofollow">Download Jesus Says — Free</a>
  </section>
</main>
</body>
</html>

Rules:
- Keep all scripture references from the original page
- Warm, theologically sound, non-preachy tone
- 800-1000 words total body content
- Every H2 must stand alone as a complete answer to a specific question"""


def upgrade(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{
            "role": "user",
            "content": f"Upgrade this page (slug: {path.stem}):\n\n{original}"
        }]
    )
    path.write_text(response.content[0].text, encoding="utf-8")


SKIP = {"index.html", "keyword-clusters.html"}

if __name__ == "__main__":
    pages = sorted(p for p in Path("content").glob("*.html") if p.name not in SKIP)
    if sys.argv[1:]:
        pages = [Path(sys.argv[1])]
    for page in pages:
        print(f"Upgrading {page.name}...", end=" ", flush=True)
        upgrade(page)
        print("done")
    print(f"\nUpgraded {len(pages)} pages.")
