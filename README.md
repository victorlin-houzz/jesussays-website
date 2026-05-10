# Jesus Says — SEO/AEO Content Site

Static content site on GitHub Pages that drives organic Christian search traffic to the [Jesus Says Now iOS app](https://apps.apple.com/us/app/jesus-says-now/id6756906208) and social channels.

- **Live site:** https://jesussays.app
- **App Store:** https://apps.apple.com/us/app/jesus-says-now/id6756906208
- **X:** https://x.com/JesusSaysNow
- **TikTok:** https://www.tiktok.com/@jesus.says.now889

---

## Architecture

```
jesussays-website/
├── index.html                  # Marketing landing page (uses landing.css)
├── download.html               # App showcase — screenshots + features
├── assets/
│   ├── landing.css             # Full design system — used by ALL pages
│   ├── site.css                # Legacy only — do NOT use for new pages
│   ├── fonts/                  # Self-hosted Lato + Merriweather woff2
│   ├── screens/                # WebP + PNG app screenshots for landing page
│   └── screenshots/            # Older web-optimized screenshots (369×800px)
├── content/
│   ├── *.html                  # AEO article pages (all use landing.css)
│   ├── index.html              # Faith Library index (uses landing.css)
│   ├── keyword-clusters.html   # SEO keyword roadmap
│   └── queue.json              # Keyword publishing queue
├── scripts/
│   ├── generate_article.py     # Local generator — uses claude CLI (no API key)
│   ├── generate_article_api.py # GHA generator — uses Anthropic SDK + API key
│   ├── check_aeo.py            # AEO validator — validates all content pages
│   ├── upgrade_pages.py        # Batch upgrade existing pages to AEO format
│   ├── migrate_articles.py     # One-shot: migrated site.css pages to landing.css
│   └── resize_screenshots.py  # Resize App Store screenshots for web
├── .github/workflows/
│   ├── pages.yml               # Deploy on push to main
│   └── publish.yml             # Cron Mon/Wed/Fri 9am UTC — generates new article
├── llms.txt                    # Content map for AI crawlers
├── robots.txt                  # With Sitemap directive
└── sitemap.xml                 # Full URL list with priority + changefreq
```

---

## Article Page HTML Standard

Every `content/*.html` article must use `landing.css` and include the full site chrome (nav, footer, mobile menu). The generator scripts produce this automatically. If writing an article by hand, use this shell:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>[Title] — Jesus Says</title>
  <meta name="description" content="[150-160 char description]" />
  <link rel="canonical" href="https://jesussays.app/content/[slug].html" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:type" content="article" />
  <link rel="stylesheet" href="/assets/landing.css" />
  <style>
    /* Article layout — keep this block verbatim in every article */
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
    .art-page h2 { font-family: var(--serif); font-weight: 700; font-size: 20px; color: var(--ink); margin: 2.5rem 0 0.75rem; }
    .art-page h3 { font-family: var(--sans); font-weight: 700; font-size: 16px; color: var(--ink); margin: 1.5rem 0 0.4rem; }
    .art-page p { font-family: var(--serif); font-size: 17px; line-height: 1.8; color: var(--ink-soft); margin-bottom: 1.1rem; }
    .art-page ul, .art-page ol { font-family: var(--serif); font-size: 17px; line-height: 1.75; color: var(--ink-soft); padding-left: 1.5rem; margin-bottom: 1.1rem; }
    .art-page li { margin-bottom: 0.6rem; }
    .art-page strong { color: var(--ink); }
    .art-page .faq { background: var(--paper); border: 1px solid var(--line); border-radius: var(--r-lg); padding: 32px; margin: 2.5rem 0; }
    .art-page .faq h2 { margin-top: 0; }
    .art-page .app-cta { background: var(--night); border-radius: var(--r-xl); padding: 44px 36px; text-align: center; margin: 2.5rem 0; position: relative; overflow: hidden; }
    .art-page .app-cta::before { content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 0%, rgba(232,155,44,0.18), transparent 60%); }
    .art-page .app-cta > * { position: relative; }
    .art-page .app-cta h2 { font-family: var(--serif); font-weight: 700; font-size: clamp(20px, 2.5vw, 28px); color: #fff; margin: 0 0 10px; }
    .art-page .app-cta p { font-family: var(--sans); font-size: 15px; color: rgba(246,241,228,0.75); margin: 0 auto 24px; }
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
      {"@type": "Article", ...},
      {"@type": "FAQPage", "mainEntity": [... 5 Q&As ...]},
      {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://jesussays.app/"},
        {"@type": "ListItem", "position": 2, "name": "Faith Library", "item": "https://jesussays.app/content/"},
        {"@type": "ListItem", "position": 3, "name": "[title]", "item": "https://jesussays.app/content/[slug].html"}
      ]}
    ]
  }
  </script>
</head>
<body>
  <!-- mobile-menu overlay, nav-wrap, main > div.art-page, footer.site, mobile-menu JS -->
  <!-- See generate_article.py for the full static chrome -->
</body>
</html>
```

**Key rules:**
- Always `<link rel="stylesheet" href="/assets/landing.css" />` — never `site.css`
- Canonical URL: `https://jesussays.app/content/[slug].html`
- Body content uses `<div class="art-page">` wrapper
- Breadcrumb includes the `/content/` middle node
- App CTA uses `class="btn-apple"` (not the old `.cta` class)
- UTM campaign: `utm_campaign=content-[slug]` on the article CTA

The generator scripts (`generate_article.py` / `generate_article_api.py`) embed the complete nav, footer, and mobile menu JS automatically. If editing existing articles manually, copy the chrome from `content/index.html`.

The `art-back` breadcrumb always links to `/content/` (the Faith Library), not to `/` (home). This is intentional — users browsing articles should navigate up to the library, not back to the marketing landing page. The nav "Faith Library" link also points to `/content/`, not `/#library`.

---

## Publishing Pipeline

### Automated (GitHub Actions)

Every Monday, Wednesday, Friday at 9am UTC:
1. `publish.yml` picks the next `"pending"` keyword from `content/queue.json`
2. Calls Anthropic API (`claude-opus-4-5`) with AEO article prompt
3. Writes `content/<slug>.html`, updates `sitemap.xml`, `llms.txt`, and `queue.json`
4. Commits and pushes → triggers `pages.yml` deploy

**Required GitHub secrets:**
- `ARTICLES_PAT` — Personal Access Token with `repo` scope (so push triggers pages.yml)
- `ANTHROPIC_API_KEY` — Anthropic API key for article generation

### Local (no API key needed)

```bash
# Generate one article using claude CLI
python3 scripts/generate_article.py

# Validate all content pages pass AEO checks
python3 scripts/check_aeo.py

# Upgrade existing pages to AEO format (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-ant-... python3 scripts/upgrade_pages.py
```

---

## AEO Content Standard

Every article page must pass `scripts/check_aeo.py`:

| Check | Requirement |
|---|---|
| `<h1>` | Present |
| Canonical link | `https://jesussays.app/content/[slug].html` |
| Meta description | Present with content |
| Article JSON-LD | `@type: Article` in `@graph` |
| FAQPage JSON-LD | `@type: FAQPage` with 5 Q&As |
| App Store link | Points to `jesus-says-now` |
| FAQ section | `<h2>Frequently Asked Questions</h2>` |
| Direct answer | First `<p>` is 10-80 words, answers immediately |

```bash
python3 scripts/check_aeo.py
# Expected: all pages pass AEO checks.
```

---

## Keyword Queue

`content/queue.json` drives the publishing pipeline. Keywords with higher `volume_est` are prioritized at the front of the queue. Add new keywords by inserting a JSON object:

```json
{"keyword": "bible verse for betrayal by a friend", "slug": "bible-verse-for-betrayal-by-a-friend", "status": "pending", "volume_est": 2100}
```

Status values: `pending` → `published`. The generator skips `published` items.

---

## Initial GitHub Setup

1. **Create GitHub Personal Access Token:**
   - Go to `https://github.com/settings/tokens/new`
   - Name: `Jesus Says Bot` · Scope: `repo`
   - Copy the token

2. **Add secrets** (repo → Settings → Secrets → Actions):
   - `ARTICLES_PAT` = PAT token above
   - `ANTHROPIC_API_KEY` = your Anthropic key

3. **Push and verify:**
   ```bash
   git push -u origin main
   ```
   Go to Actions tab → verify `pages.yml` deploys successfully.

4. **Enable GitHub Pages** (if not already):
   - Repo → Settings → Pages → Source: **GitHub Actions**

5. **Trigger first article run:**
   - Actions → "Publish New Article" → Run workflow

---

## Social Media Strategy

Each new article maps to cross-platform content:

| Asset | Platform | Format |
|---|---|---|
| Blog article | Website | AEO HTML with FAQPage schema |
| Hook quote from article | X/Twitter | Thread with app link in reply |
| Top verse from article | TikTok | Fact slideshow, 5 slides, trending audio |
| "What would Jesus say about X" pages | TikTok | Voiceover + on-screen text, 45-60 sec |
| Comment replies | TikTok | Stitch/reply directing to app download |

**High-converting TikTok hooks (from PrayScreen case study):**
- "If a friend betrayed you, Jesus said exactly this."
- "The Bible verse churches never preach — but Jesus said constantly."
- "This prayer changed my week in 3 days — here's exactly what I said."

**X thread format:**
1. Hook tweet (contrarian or foreshadowing)
2. 3-5 verse tweets with brief context
3. Reply with app link + UTM

---

## Paywall Conversion

Premium features that drive upgrades (from Glorify/Hallow data):
- Interactive confession prayer sequences
- Personalized "what would Jesus say" responses
- Guided prayer audio
- Streak/habit tracking

Blog content that converts:
- **Confession pages** → highest intent (user is in vulnerable, seeking moment)
- **"What would Jesus say about X"** → interactive app feature is the natural next step
- **Daily devotional pages** → habit formation → subscription feels natural

App Store link always uses UTM tracking:
```
?utm_source=website&utm_medium=cta&utm_campaign=content-[slug]
```
For homepage hero: `utm_campaign=home-hero`
For download page: `utm_campaign=download-hero`

---

## Hermes Agent Loop

See `HERMES_AGENT.md` for the full daily/weekly agent playbook used by the automated publishing agent.
