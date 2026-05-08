# Jesus Says Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the existing skeleton site into a fully AEO-optimized Christian content hub with an automated publishing pipeline that generates 3 new articles per week via GitHub Actions + Claude API.

**Architecture:** Static HTML/CSS on GitHub Pages. All 22 existing pages are batch-upgraded to AEO template via a Python + Claude API script. A keyword queue (`content/queue.json`) drives a cron workflow (Mon/Wed/Fri 9am UTC) that generates, commits, and pushes one new article per run — which triggers the existing `pages.yml` deploy. App screenshots are web-optimized and used on the homepage and a new `/download.html` page.

**Tech Stack:** Plain HTML/CSS, Python 3.12, Anthropic SDK (`anthropic`), Pillow (`Pillow`), GitHub Actions, GitHub Pages

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `assets/site.css` | Readability: 18px body, 1.7 line-height, 680px max-width, .faq/.app-cta blocks |
| Modify | `robots.txt` | Add `Sitemap:` directive |
| Modify | `sitemap.xml` | Add `<priority>` + `<changefreq>` to all URLs |
| Modify | `llms.txt` | Expand to full site map with all categories |
| Create | `assets/screenshots/screenshot-01..06.png` | Web-optimized app screenshots (max height 800px) |
| Create | `download.html` | App showcase with all 6 screenshots + feature list |
| Modify | `index.html` | Real App Store link + UTM, 5 content categories, screenshot preview |
| Create | `scripts/check_aeo.py` | Validate pages have h1, canonical, meta desc, Article + FAQPage schema, App Store link, FAQ h2, direct-answer ≤80 words |
| Create | `scripts/upgrade_pages.py` | Calls Claude API to rewrite all 20 article pages to AEO template |
| Create | `scripts/requirements.txt` | `anthropic`, `Pillow` |
| Create | `content/queue.json` | 30-item ordered keyword queue |
| Create | `scripts/generate_article.py` | Picks next queued keyword → generates AEO HTML → updates sitemap + llms.txt + queue |
| Create | `.github/workflows/publish.yml` | Cron Mon/Wed/Fri: run generate_article.py, commit + push with PAT |

---

### Task 1: CSS Readability Upgrade

**Files:**
- Modify: `assets/site.css`

- [ ] **Step 1: Replace site.css**

Replace the entire file with:

```css
:root {
  --max: 680px;
  --ink: #1a1a1a;
  --link: #1a4fa0;
  --blue: #2563eb;
  --bg: #fafaf8;
  --border: #e5e7eb;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 18px; line-height: 1.7; color: var(--ink); background: var(--bg); }
.container { max-width: var(--max); margin: 0 auto; padding: 2rem 1.25rem; }
h1 { font-size: 2rem; line-height: 1.25; margin-bottom: 1rem; }
h2 { font-size: 1.35rem; margin: 2rem 0 0.75rem; }
h3 { font-size: 1.1rem; margin: 1.5rem 0 0.4rem; }
p { margin-bottom: 1rem; }
ul, ol { padding-left: 1.5rem; margin-bottom: 1rem; }
li { margin-bottom: 0.4rem; }
a { color: var(--link); }
a:hover { text-decoration: none; }
.cta { display: inline-block; background: var(--blue); color: #fff; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; font-family: system-ui, sans-serif; font-weight: 600; margin: 0.5rem 0; }
.cta:hover { background: #1d4ed8; }
header { border-bottom: 1px solid var(--border); padding: 3rem 1.25rem 2rem; }
header .eyebrow { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; color: #666; font-family: system-ui, sans-serif; margin-bottom: 0.5rem; }
footer { border-top: 1px solid var(--border); padding: 1.5rem 1.25rem; font-size: 0.9rem; color: #666; font-family: system-ui, sans-serif; }
.faq { background: #f0f4ff; padding: 1.5rem; border-radius: 8px; margin: 2rem 0; }
.faq h2 { margin-top: 0; }
.app-cta { background: #fff; border: 2px solid var(--border); border-radius: 12px; padding: 1.5rem; margin: 2.5rem 0; text-align: center; }
.app-cta h2 { margin-top: 0; }
.app-cta p { margin-bottom: 0.75rem; }
.screenshots { display: flex; gap: 1rem; overflow-x: auto; padding: 1rem 0; scroll-snap-type: x mandatory; }
.screenshots img { height: 400px; width: auto; border-radius: 20px; box-shadow: 0 4px 24px rgba(0,0,0,0.15); scroll-snap-align: start; flex-shrink: 0; }
section { margin-bottom: 2.5rem; }
@media (max-width: 600px) {
  body { font-size: 16px; }
  h1 { font-size: 1.6rem; }
  .screenshots img { height: 300px; }
}
```

- [ ] **Step 2: Commit**

```bash
git add assets/site.css
git commit -m "style: readability upgrade — 18px body, 1.7 line-height, faq/cta blocks"
```

---

### Task 2: Infrastructure Files

**Files:**
- Modify: `robots.txt`
- Modify: `sitemap.xml`
- Modify: `llms.txt`

- [ ] **Step 1: Update robots.txt**

Replace the file with:

```
User-agent: *
Allow: /

Sitemap: https://victorlin-houzz.github.io/jesussays-website/sitemap.xml
```

- [ ] **Step 2: Add priority + changefreq to every sitemap URL**

Open `sitemap.xml`. For each `<url>` block, add two child elements so every entry looks like this example:

```xml
<url>
  <loc>https://victorlin-houzz.github.io/jesussays-website/content/bible-verses-anxiety.html</loc>
  <lastmod>2026-05-08</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

The root `<url>` (the homepage) should have `<priority>1.0</priority>` and `<changefreq>weekly</changefreq>`. All content pages get `0.8` / `monthly`.

- [ ] **Step 3: Replace llms.txt**

```
# Jesus Says Content Map for AI Crawlers

Jesus Says is a Christian guidance content website. Primary focus: Bible verse discovery, prayer support, confession guidance, daily devotion, and practical Christian advice.

## Bible Verse Articles
- /content/bible-verses-anxiety.html — Bible verses for anxiety and worry
- /content/bible-verses-for-strength-hard-times.html — Bible verses for strength in hard times
- /content/bible-verses-about-faith-and-trust.html — Bible verses about faith and trust
- /content/bible-verses-about-peace-and-fear.html — Bible verses about peace and fear

## Prayer Guides
- /content/prayer-for-healing.html — Prayer for healing with Scripture
- /content/how-to-pray-according-to-the-bible.html — How to pray according to the Bible
- /content/morning-prayer-for-protection.html — Morning prayer for protection
- /content/night-prayer-for-sleep-and-anxiety.html — Night prayer for sleep and anxiety
- /content/prayer-for-depression-and-hopelessness.html — Prayer for depression and hopelessness
- /content/prayer-for-family-and-marriage.html — Prayer for family and marriage

## Confession + Forgiveness
- /content/confession-prayer-guide.html — Confession prayer guide with Psalm 51
- /content/confession-prayer-after-failure.html — Confession prayer after failure or shame
- /content/confession-prayer-for-addiction-recovery.html — Confession prayer for addiction recovery
- /content/love-and-forgiveness.html — Love and forgiveness in Scripture

## Daily Devotionals
- /content/daily-devotional-today.html — Daily devotional for today
- /content/daily-devotional-on-financial-stress.html — Daily devotional on financial stress
- /content/daily-devotional-on-forgiveness.html — Daily devotional on forgiveness
- /content/daily-devotional-on-purpose.html — Daily devotional on purpose and calling

## Christian Advice
- /content/christian-advice-for-relationships.html — Christian advice for relationships
- /content/christian-advice-for-anxiety-at-work.html — Christian advice for anxiety at work
- /content/jesus-quotes-on-love-mercy-and-truth.html — Jesus quotes on love, mercy, and truth

## Primary Intent Coverage
- Bible verses for anxiety, healing, strength, faith, peace, fear
- Daily devotional for today, financial stress, forgiveness, purpose
- Confession prayer, Psalm 51, addiction recovery, failure
- Christian advice for relationships, work anxiety, love
- Prayer for healing, depression, family, morning, night

## Conversion Goal
Route engaged readers to the Jesus Says iOS app for personalized scripture, voice prayer, and devotional journaling.
App Store: https://apps.apple.com/us/app/jesus-says-now/id6756906208
```

- [ ] **Step 4: Commit**

```bash
git add robots.txt sitemap.xml llms.txt
git commit -m "seo: add sitemap directive, priority/changefreq, expand llms.txt"
```

---

### Task 3: Copy and Web-Optimize App Screenshots

**Files:**
- Create: `scripts/resize_screenshots.py`
- Create: `assets/screenshots/screenshot-01.png` through `screenshot-06.png`

- [ ] **Step 1: Create resize script**

Create `scripts/resize_screenshots.py`:

```python
#!/usr/bin/env python3
"""Resize App Store screenshots to web size (max height 800px)."""
from pathlib import Path
from PIL import Image

src = Path.home() / "Desktop/jesussays_appstore_submission/submission_2026_04_28/iphone_1290x2796"
dst = Path("assets/screenshots")
dst.mkdir(parents=True, exist_ok=True)

pngs = sorted(src.glob("*.png"))
assert len(pngs) == 6, f"Expected 6 screenshots, found {len(pngs)}"

for i, png in enumerate(pngs, 1):
    img = Image.open(png)
    w, h = img.size
    new_h = 800
    new_w = round(w * new_h / h)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    out = dst / f"screenshot-{i:02d}.png"
    img.save(out, optimize=True)
    size_kb = out.stat().st_size // 1024
    print(f"screenshot-{i:02d}.png  {new_w}×{new_h}  {size_kb}KB")

print(f"\nSaved {len(pngs)} screenshots to {dst}/")
```

- [ ] **Step 2: Install Pillow and run**

```bash
pip install Pillow
python scripts/resize_screenshots.py
```

Expected output:
```
screenshot-01.png  370×800  ...KB
screenshot-02.png  370×800  ...KB
screenshot-03.png  370×800  ...KB
screenshot-04.png  370×800  ...KB
screenshot-05.png  370×800  ...KB
screenshot-06.png  370×800  ...KB

Saved 6 screenshots to assets/screenshots/
```

- [ ] **Step 3: Commit**

```bash
git add assets/screenshots/
git commit -m "assets: add web-optimized app screenshots (6 × 370×800px)"
```

---

### Task 4: Create download.html App Showcase Page

**Files:**
- Create: `download.html`

- [ ] **Step 1: Write download.html**

Create `download.html` in the project root:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Download Jesus Says — Bible Verses, Prayer &amp; Daily Devotion App</title>
  <meta name="description" content="Jesus Says brings personalized Bible verses, voice prayer, confession journaling, and daily devotionals to your iPhone. Free to download on the App Store." />
  <meta name="keywords" content="jesus says app, bible app, daily devotional app, prayer app, christian app" />
  <link rel="canonical" href="https://victorlin-houzz.github.io/jesussays-website/download.html" />
  <link rel="stylesheet" href="/jesussays-website/assets/site.css" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "MobileApplication",
    "name": "Jesus Says Now",
    "operatingSystem": "iOS",
    "applicationCategory": "LifestyleApplication",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    "url": "https://apps.apple.com/us/app/jesus-says-now/id6756906208",
    "description": "Personalized Bible verses, voice prayer, confession journaling, and daily devotionals."
  }
  </script>
</head>
<body>
  <header class="container">
    <p class="eyebrow"><a href="/jesussays-website/">Jesus Says</a></p>
    <h1>Your Daily Faith Companion</h1>
    <p>Receive personalized Bible verses for your exact moment. Talk to Jesus by voice. Journal your confessions. Build a daily faith rhythm — one day at a time.</p>
    <p><a class="cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=download-hero" rel="nofollow">Download on the App Store — Free</a></p>
  </header>

  <main class="container">
    <section>
      <h2>What Jesus Says Does</h2>
      <ol>
        <li><strong>Build a Daily Faith Rhythm</strong> — Start every morning with Scripture, prayer, and reflection built into a simple, sustainable habit.</li>
        <li><strong>Read the Bible Verse by Verse</strong> — Explore Scripture at your own pace with guided reading tailored to where you are spiritually.</li>
        <li><strong>Find Where to Start in Scripture</strong> — Not sure where to begin? Jesus Says recommends passages for your exact situation and season.</li>
        <li><strong>Talk to Jesus by Voice</strong> — Speak your prayers and struggles aloud and receive Scripture-anchored responses in return.</li>
        <li><strong>A Sacred Space for Personal Reflection</strong> — Journal your confessions, prayers, and gratitude in a private, faith-centered space.</li>
        <li><strong>Receive Scripture for Your Exact Moment</strong> — Whether you're anxious, grieving, or full of hope, get the verse that speaks to right now.</li>
      </ol>
    </section>

    <section>
      <h2>See It in Action</h2>
      <div class="screenshots">
        <img src="/jesussays-website/assets/screenshots/screenshot-01.png" alt="Build a Daily Faith Rhythm — Jesus Says app" width="370" height="800" loading="lazy" />
        <img src="/jesussays-website/assets/screenshots/screenshot-02.png" alt="Read the Bible Verse by Verse — Jesus Says app" width="370" height="800" loading="lazy" />
        <img src="/jesussays-website/assets/screenshots/screenshot-03.png" alt="Find Where to Start in Scripture — Jesus Says app" width="370" height="800" loading="lazy" />
        <img src="/jesussays-website/assets/screenshots/screenshot-04.png" alt="Talk to Jesus by Voice — Jesus Says app" width="370" height="800" loading="lazy" />
        <img src="/jesussays-website/assets/screenshots/screenshot-05.png" alt="A Sacred Space for Personal Reflection — Jesus Says app" width="370" height="800" loading="lazy" />
        <img src="/jesussays-website/assets/screenshots/screenshot-06.png" alt="Receive Scripture for Your Exact Moment — Jesus Says app" width="370" height="800" loading="lazy" />
      </div>
      <p><a class="cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=download-screenshots" rel="nofollow">Download Jesus Says — Free</a></p>
    </section>

    <section>
      <h2>Available For</h2>
      <ul>
        <li>iPhone — free to download on the App Store</li>
        <li>Morning devotionals and evening reflection</li>
        <li>Voice prayer with Scripture-based responses</li>
        <li>Confession journaling in a private, sacred space</li>
        <li>Personalized Bible verse discovery</li>
      </ul>
    </section>
  </main>

  <footer class="container">
    <p>© Jesus Says · <a href="/jesussays-website/">Back to Content Library</a></p>
  </footer>
</body>
</html>
```

- [ ] **Step 2: Add download.html to sitemap.xml**

In `sitemap.xml`, add before the closing `</urlset>`:

```xml
  <url>
    <loc>https://victorlin-houzz.github.io/jesussays-website/download.html</loc>
    <lastmod>2026-05-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
```

- [ ] **Step 3: Commit**

```bash
git add download.html sitemap.xml
git commit -m "feat: add download.html app showcase with 6 screenshots"
```

---

### Task 5: Upgrade Homepage (index.html)

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Replace index.html**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Jesus Says — Bible Verses, Prayer, Confession, Daily Devotion</title>
  <meta name="description" content="Find Bible verses for anxiety, healing, and strength. Prayers for every need. Daily devotionals. Confession guides. Practical Christian advice with Scripture." />
  <meta name="keywords" content="bible verses, jesus says, prayer, daily devotional, confession, christian advice, bible study" />
  <link rel="canonical" href="https://victorlin-houzz.github.io/jesussays-website/" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:title" content="Jesus Says — Bible Verses, Prayer, Devotion, Christian Advice" />
  <meta property="og:description" content="Practical faith guidance with Scripture. Bible verses for every situation, prayers for every need, daily devotionals, and Christian advice for real life." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://victorlin-houzz.github.io/jesussays-website/" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="stylesheet" href="/jesussays-website/assets/site.css" />
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"WebSite","name":"Jesus Says","url":"https://victorlin-houzz.github.io/jesussays-website/","description":"Christian content hub with Bible verses, prayer guides, daily devotionals, and faith-based advice."}
  </script>
</head>
<body>
  <header class="container">
    <p class="eyebrow">Jesus Says</p>
    <h1>Faith Answers for Real Life</h1>
    <p>Bible verses for anxiety, healing, grief, and strength. Prayers for every season. Daily devotionals. Confession guides. Christian advice grounded in Scripture.</p>
    <p><a class="cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=homepage-hero" rel="nofollow">Download the Jesus Says App — Free</a></p>
  </header>

  <main class="container">
    <section>
      <h2>Bible Verses by Situation</h2>
      <ul>
        <li><a href="/jesussays-website/content/bible-verses-anxiety.html">Bible verses for anxiety and worry</a></li>
        <li><a href="/jesussays-website/content/bible-verses-for-strength-hard-times.html">Bible verses for strength in hard times</a></li>
        <li><a href="/jesussays-website/content/bible-verses-about-faith-and-trust.html">Bible verses about faith and trust</a></li>
        <li><a href="/jesussays-website/content/bible-verses-about-peace-and-fear.html">Bible verses about peace and fear</a></li>
      </ul>
    </section>

    <section>
      <h2>Prayer Guides</h2>
      <ul>
        <li><a href="/jesussays-website/content/prayer-for-healing.html">Prayer for healing with Scripture</a></li>
        <li><a href="/jesussays-website/content/how-to-pray-according-to-the-bible.html">How to pray according to the Bible</a></li>
        <li><a href="/jesussays-website/content/morning-prayer-for-protection.html">Morning prayer for protection</a></li>
        <li><a href="/jesussays-website/content/night-prayer-for-sleep-and-anxiety.html">Night prayer for sleep and anxiety</a></li>
        <li><a href="/jesussays-website/content/prayer-for-depression-and-hopelessness.html">Prayer for depression and hopelessness</a></li>
        <li><a href="/jesussays-website/content/prayer-for-family-and-marriage.html">Prayer for family and marriage</a></li>
      </ul>
    </section>

    <section>
      <h2>Confession + Forgiveness</h2>
      <ul>
        <li><a href="/jesussays-website/content/confession-prayer-guide.html">Confession prayer guide (Psalm 51)</a></li>
        <li><a href="/jesussays-website/content/confession-prayer-after-failure.html">Confession prayer after failure</a></li>
        <li><a href="/jesussays-website/content/confession-prayer-for-addiction-recovery.html">Confession prayer for addiction recovery</a></li>
        <li><a href="/jesussays-website/content/love-and-forgiveness.html">Love and forgiveness in Scripture</a></li>
      </ul>
    </section>

    <section>
      <h2>Daily Devotionals</h2>
      <ul>
        <li><a href="/jesussays-website/content/daily-devotional-today.html">Daily devotional for today</a></li>
        <li><a href="/jesussays-website/content/daily-devotional-on-financial-stress.html">Daily devotional on financial stress</a></li>
        <li><a href="/jesussays-website/content/daily-devotional-on-forgiveness.html">Daily devotional on forgiveness</a></li>
        <li><a href="/jesussays-website/content/daily-devotional-on-purpose.html">Daily devotional on purpose and calling</a></li>
      </ul>
    </section>

    <section>
      <h2>Christian Advice + Guidance</h2>
      <ul>
        <li><a href="/jesussays-website/content/christian-advice-for-relationships.html">Christian advice for relationships</a></li>
        <li><a href="/jesussays-website/content/christian-advice-for-anxiety-at-work.html">Christian advice for anxiety at work</a></li>
        <li><a href="/jesussays-website/content/jesus-quotes-on-love-mercy-and-truth.html">Jesus quotes on love, mercy, and truth</a></li>
      </ul>
    </section>

    <section>
      <h2>Get the Jesus Says App</h2>
      <p>Talk to Jesus by voice. Receive Bible verses for your exact moment. Build a daily faith rhythm with devotionals, prayer prompts, and personal reflection.</p>
      <div class="screenshots">
        <img src="/jesussays-website/assets/screenshots/screenshot-01.png" alt="Build a Daily Faith Rhythm — Jesus Says app" width="370" height="800" loading="lazy" />
        <img src="/jesussays-website/assets/screenshots/screenshot-04.png" alt="Talk to Jesus by Voice — Jesus Says app" width="370" height="800" loading="lazy" />
        <img src="/jesussays-website/assets/screenshots/screenshot-06.png" alt="Receive Scripture for Your Exact Moment — Jesus Says app" width="370" height="800" loading="lazy" />
      </div>
      <p><a class="cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=homepage-screenshots" rel="nofollow">Download on the App Store — Free</a></p>
      <p><a href="/jesussays-website/download.html">See all app features →</a></p>
    </section>
  </main>

  <footer class="container">
    <p>© Jesus Says · <a href="/jesussays-website/download.html">About the App</a> · <a href="/jesussays-website/content/index.html">Full Article Library</a></p>
  </footer>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat: upgrade homepage with real App Store link, UTM, 5 content categories, screenshot preview"
```

---

### Task 6: Write AEO Validator

**Files:**
- Create: `scripts/check_aeo.py`

This is the test harness. Run it before and after the page upgrade to confirm all pages pass.

- [ ] **Step 1: Create scripts/check_aeo.py**

```python
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
```

- [ ] **Step 2: Run validator (expect failures — this is the TDD baseline)**

```bash
python scripts/check_aeo.py
```

Expected: Most pages FAIL with issues like "missing FAQPage JSON-LD", "missing FAQ section h2", "missing App Store link". Exit code 1. Note the count — you'll confirm all pass after Task 7.

- [ ] **Step 3: Commit**

```bash
git add scripts/check_aeo.py
git commit -m "test: add AEO validator (check_aeo.py)"
```

---

### Task 7: Batch Upgrade Existing Content Pages

**Files:**
- Create: `scripts/upgrade_pages.py`
- Modify: all 20 article pages in `content/` (excluding `index.html` and `keyword-clusters.html`)
- Create: `scripts/requirements.txt`

- [ ] **Step 1: Create scripts/requirements.txt**

```
anthropic>=0.28.0
Pillow>=10.0.0
```

- [ ] **Step 2: Install dependencies**

```bash
pip install -r scripts/requirements.txt
```

- [ ] **Step 3: Create scripts/upgrade_pages.py**

```python
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
```

- [ ] **Step 4: Run upgrade script (this calls Claude API ~20 times, ~$0.30 at current pricing)**

```bash
ANTHROPIC_API_KEY=<your-key> python scripts/upgrade_pages.py
```

Expected output (one line per page):
```
Upgrading bible-verses-about-faith-and-trust.html... done
Upgrading bible-verses-about-peace-and-fear.html... done
...
Upgraded 20 pages.
```

- [ ] **Step 5: Run AEO validator — all pages must now pass**

```bash
python scripts/check_aeo.py
```

Expected output: `20/20 pages pass AEO checks.` — exit code 0. If any FAIL, re-run upgrade on that single file: `python scripts/upgrade_pages.py content/<failing-page>.html`

- [ ] **Step 6: Commit**

```bash
git add scripts/ content/
git commit -m "feat: upgrade all 20 content pages to AEO format (FAQPage schema, direct answer, FAQ section)"
```

---

### Task 8: Create Keyword Queue

**Files:**
- Create: `content/queue.json`

- [ ] **Step 1: Write content/queue.json**

```json
[
  {"keyword": "bible verses for anxiety about money", "slug": "bible-verses-for-anxiety-about-money", "status": "pending"},
  {"keyword": "bible verses for job loss and unemployment", "slug": "bible-verses-for-job-loss-and-unemployment", "status": "pending"},
  {"keyword": "bible verses for loneliness and isolation", "slug": "bible-verses-for-loneliness-and-isolation", "status": "pending"},
  {"keyword": "bible verses for going through divorce", "slug": "bible-verses-for-going-through-divorce", "status": "pending"},
  {"keyword": "bible verses for chronic illness and suffering", "slug": "bible-verses-for-chronic-illness-and-suffering", "status": "pending"},
  {"keyword": "bible verses for infertility and loss", "slug": "bible-verses-for-infertility-and-loss", "status": "pending"},
  {"keyword": "bible verses for grief and losing a parent", "slug": "bible-verses-for-grief-and-losing-a-parent", "status": "pending"},
  {"keyword": "short prayer for a friend with cancer", "slug": "short-prayer-for-friend-with-cancer", "status": "pending"},
  {"keyword": "prayer before surgery for peace", "slug": "prayer-before-surgery-for-peace", "status": "pending"},
  {"keyword": "prayer for financial breakthrough", "slug": "prayer-for-financial-breakthrough", "status": "pending"},
  {"keyword": "prayer for clarity in a difficult decision", "slug": "prayer-for-clarity-in-difficult-decision", "status": "pending"},
  {"keyword": "bedtime prayer for children with anxiety", "slug": "bedtime-prayer-for-children-with-anxiety", "status": "pending"},
  {"keyword": "prayer for someone with addiction", "slug": "prayer-for-someone-with-addiction", "status": "pending"},
  {"keyword": "daily devotional for new moms", "slug": "daily-devotional-for-new-moms", "status": "pending"},
  {"keyword": "morning devotional for men in recovery", "slug": "morning-devotional-for-men-in-recovery", "status": "pending"},
  {"keyword": "daily devotional for single women trusting God", "slug": "daily-devotional-for-single-women-trusting-god", "status": "pending"},
  {"keyword": "devotional for teens with anxiety", "slug": "devotional-for-teens-with-anxiety", "status": "pending"},
  {"keyword": "daily devotional for grief", "slug": "daily-devotional-for-grief", "status": "pending"},
  {"keyword": "what does the Bible say about depression", "slug": "what-does-the-bible-say-about-depression", "status": "pending"},
  {"keyword": "what does the Bible say about comparison and envy", "slug": "what-does-the-bible-say-about-comparison-and-envy", "status": "pending"},
  {"keyword": "what does the Bible say about social media", "slug": "what-does-the-bible-say-about-social-media", "status": "pending"},
  {"keyword": "what does the Bible say about debt and money", "slug": "what-does-the-bible-say-about-debt-and-money", "status": "pending"},
  {"keyword": "what does the Bible say about digital rest and Sabbath", "slug": "what-does-the-bible-say-about-digital-rest-sabbath", "status": "pending"},
  {"keyword": "Christian advice for setting dating boundaries", "slug": "christian-advice-for-setting-dating-boundaries", "status": "pending"},
  {"keyword": "Christian mindfulness vs secular mindfulness", "slug": "christian-mindfulness-vs-secular-mindfulness", "status": "pending"},
  {"keyword": "Christian advice for digital burnout and screen time", "slug": "christian-advice-for-digital-burnout-screen-time", "status": "pending"},
  {"keyword": "what the Bible says about loneliness in marriage", "slug": "bible-verses-for-loneliness-in-marriage", "status": "pending"},
  {"keyword": "how to pray for a prodigal child", "slug": "how-to-pray-for-prodigal-child", "status": "pending"},
  {"keyword": "Christian grief counseling what Scripture says", "slug": "christian-grief-counseling-scripture", "status": "pending"},
  {"keyword": "bible verses for new beginnings and fresh start", "slug": "bible-verses-for-new-beginnings-fresh-start", "status": "pending"}
]
```

- [ ] **Step 2: Commit**

```bash
git add content/queue.json
git commit -m "content: add 30-item AEO keyword queue"
```

---

### Task 9: Create Article Generator Script

**Files:**
- Create: `scripts/generate_article.py`

- [ ] **Step 1: Write scripts/generate_article.py**

```python
#!/usr/bin/env python3
"""Generate one AEO article from the keyword queue and update site files."""
import json
import re
import sys
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

import anthropic

client = anthropic.Anthropic()

SYSTEM = """You are an AEO content writer for Jesus Says, a Christian guidance website.
Write warm, theologically sound, practical content. Target 900-1100 words of body content.

Output ONLY raw HTML — no markdown fences, no explanation.

Required structure:
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>[H1 Title] — Jesus Says 2026</title>
  <meta name="description" content="[150-160 char answer-first description]">
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
        "datePublished": "[YYYY-MM-DD]",
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
  <h1>[Title]</h1>
  <p>[Direct answer: 40-60 words, no preamble, answers immediately]</p>
  <h2>[Primary sub-question as H2, e.g. "What does the Bible say about X?"]</h2>
  <ol>
    <li><strong>Book Chapter:Verse</strong> — "exact verse text." One-sentence application.</li>
    [4-6 verses]
  </ol>
  <h2>[Practical question: "How to X when Y"]</h2>
  <ol>
    <li>[Specific actionable step]</li>
    [3-5 steps]
  </ol>
  <h2>[Third follow-up question]</h2>
  <p>[40-60 word atomic answer]</p>
  <section class="faq">
    <h2>Frequently Asked Questions</h2>
    <h3>[Q1]</h3><p>[40-60 word answer]</p>
    <h3>[Q2]</h3><p>[40-60 word answer]</p>
    <h3>[Q3]</h3><p>[40-60 word answer]</p>
    <h3>[Q4]</h3><p>[40-60 word answer]</p>
    <h3>[Q5]</h3><p>[40-60 word answer]</p>
  </section>
  <section class="app-cta">
    <h2>Get Daily Scripture for Your Exact Moment</h2>
    <p>Jesus Says brings personalized Bible verses, prayer prompts, and confession journaling to your phone.</p>
    <a class="cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&utm_medium=cta&utm_campaign=organic" rel="nofollow">Download Jesus Says — Free</a>
  </section>
</main>
</body>
</html>"""

QUEUE_PATH = Path("content/queue.json")
SITEMAP_PATH = Path("sitemap.xml")
LLMS_PATH = Path("llms.txt")
BASE_URL = "https://victorlin-houzz.github.io/jesussays-website"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def load_queue() -> list[dict]:
    return json.loads(QUEUE_PATH.read_text())


def save_queue(queue: list[dict]) -> None:
    QUEUE_PATH.write_text(json.dumps(queue, indent=2) + "\n")


def next_item(queue: list[dict]) -> dict | None:
    return next((q for q in queue if q["status"] == "pending"), None)


def generate_html(keyword: str, slug: str) -> str:
    today = date.today().isoformat()
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{
            "role": "user",
            "content": f'Write an AEO article.\nKeyword: "{keyword}"\nSlug: {slug}\nDate: {today}'
        }]
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
        print("Queue exhausted — nothing to publish.")
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
```

- [ ] **Step 2: Commit**

```bash
git add scripts/generate_article.py scripts/requirements.txt
git commit -m "feat: add article generator script (generate_article.py)"
```

---

### Task 10: Test Generator Locally (First 3 Articles)

- [ ] **Step 1: Set your API key and run the generator 3 times**

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/generate_article.py  # generates article #1
python scripts/generate_article.py  # generates article #2
python scripts/generate_article.py  # generates article #3
```

Each run prints something like:
```
Generating: bible verses for anxiety about money
Written: content/bible-verses-for-anxiety-about-money.html
Sitemap updated.
llms.txt updated.
Queue updated.
```

- [ ] **Step 2: Validate the 3 new pages pass AEO checks**

```bash
python scripts/check_aeo.py
```

The 3 new pages should show PASS. If any FAIL, open the file and check what's missing — likely the App Store link URL isn't matching exactly. Fix the `SYSTEM` prompt in `generate_article.py` if needed and re-generate.

- [ ] **Step 3: Commit**

```bash
git add content/ sitemap.xml llms.txt content/queue.json
git commit -m "content: publish first 3 articles from keyword queue"
```

---

### Task 11: Create GitHub Actions Publish Workflow

**Files:**
- Create: `.github/workflows/publish.yml`

- [ ] **Step 1: Write .github/workflows/publish.yml**

```yaml
name: Publish New Article

on:
  schedule:
    - cron: "0 9 * * 1,3,5"  # Mon, Wed, Fri at 9am UTC
  workflow_dispatch:           # allow manual trigger from GitHub UI

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.ARTICLES_PAT }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install anthropic

      - name: Configure git
        run: |
          git config user.name "Jesus Says Bot"
          git config user.email "swissashley@gmail.com"

      - name: Generate article
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python scripts/generate_article.py

      - name: Check for new files
        id: diff
        run: |
          git diff --quiet && git diff --cached --quiet && echo "changed=false" >> $GITHUB_OUTPUT || echo "changed=true" >> $GITHUB_OUTPUT

      - name: Commit and push
        if: steps.diff.outputs.changed == 'true'
        run: |
          git add content/ sitemap.xml llms.txt content/queue.json
          git commit -m "content: publish $(date +%Y-%m-%d) article"
          git push
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/publish.yml
git commit -m "ci: add Mon/Wed/Fri article publisher workflow"
```

---

### Task 12: Configure GitHub Secrets and Final Push

**No files to create — GitHub UI configuration.**

- [ ] **Step 1: Create a GitHub Personal Access Token (PAT)**

Go to: `https://github.com/settings/tokens/new`
- Token name: `Jesus Says Bot`
- Expiration: 1 year (or No expiration)
- Scopes: check `repo` (gives contents read/write + workflows)
- Click **Generate token** and copy it

- [ ] **Step 2: Add secrets to the GitHub repo**

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add two secrets:
1. Name: `ARTICLES_PAT` — Value: the PAT you just created
2. Name: `ANTHROPIC_API_KEY` — Value: your Anthropic API key (`sk-ant-...`)

- [ ] **Step 3: Verify repo is on GitHub and Pages is enabled**

```bash
git remote -v
```

If the remote doesn't exist yet, add it:

```bash
git remote add origin https://github.com/victorlin-houzz/jesussays-website.git
```

In GitHub repo settings → **Pages** → Source: **GitHub Actions** (already configured via `pages.yml`).

- [ ] **Step 4: Push everything to main**

```bash
git push -u origin main
```

- [ ] **Step 5: Verify deployment**

After ~60 seconds, open `https://victorlin-houzz.github.io/jesussays-website/` and confirm:
- New CSS is applied (18px body, card sections)
- App Store links say "Download the Jesus Says App — Free" and point to `id6756906208`
- Homepage shows 3 screenshots in a scrollable row
- `/download.html` shows all 6 screenshots

- [ ] **Step 6: Trigger a test run of the publish workflow**

In GitHub → repo → **Actions** → **Publish New Article** → **Run workflow** → **Run workflow**

Watch the run complete. Confirm a new commit appears in `main` with message `content: publish YYYY-MM-DD article`. Confirm Pages re-deploys and the new article is live.

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| CSS readability upgrade | Task 1 |
| robots.txt Sitemap directive | Task 2 |
| sitemap priority/changefreq | Task 2 |
| llms.txt expansion | Task 2 |
| App screenshots web-optimized | Task 3 |
| download.html showcase | Task 4 |
| Homepage with real App Store link + UTM + screenshots | Task 5 |
| AEO validator (TDD baseline) | Task 6 |
| Upgrade all 20 existing pages to AEO | Task 7 |
| 30-item keyword queue | Task 8 |
| Article generator (generate_article.py) | Task 9 |
| Test generator (3 articles) | Task 10 |
| GHA cron publish workflow | Task 11 |
| GitHub secrets + push | Task 12 |

All spec requirements covered. No TBDs or placeholders in code blocks.

**Type/method consistency:**
- `QUEUE_PATH`, `SITEMAP_PATH`, `LLMS_PATH` defined at module level in `generate_article.py` — used consistently throughout
- `check_aeo.py` checks for `apps.apple.com/us/app/jesus-says-now` — the same URL pattern used in all upgrade/generation scripts
- `SKIP = {"index.html", "keyword-clusters.html"}` used in both `upgrade_pages.py` and `check_aeo.py`
