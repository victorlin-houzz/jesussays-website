# Jesus Says — SEO/AEO Content Site

Static content site on GitHub Pages that drives organic Christian search traffic to the [Jesus Says Now iOS app](https://apps.apple.com/us/app/jesus-says-now/id6756906208) and social channels.

- **Live site:** https://victorlin-houzz.github.io/jesussays-website/
- **App Store:** https://apps.apple.com/us/app/jesus-says-now/id6756906208
- **X:** https://x.com/JesusSaysNow
- **TikTok:** https://www.tiktok.com/@jesus.says.now889

---

## Architecture

```
jesussays-website/
├── index.html                  # Homepage — 5 content categories + app CTA
├── download.html               # App showcase — all 6 screenshots + features
├── assets/
│   ├── site.css                # Design system (18px body, 1.7lh, 680px max)
│   └── screenshots/            # Web-optimized app screenshots (369×800px)
├── content/
│   ├── *.html                  # AEO article pages (21 existing + growing)
│   ├── index.html              # Content library index
│   ├── keyword-clusters.html   # SEO keyword roadmap
│   └── queue.json              # Keyword publishing queue
├── scripts/
│   ├── generate_article.py     # Local generator — uses claude CLI (no API key)
│   ├── generate_article_api.py # GHA generator — uses Anthropic SDK + API key
│   ├── check_aeo.py            # AEO validator — validates all content pages
│   ├── upgrade_pages.py        # Batch upgrade existing pages to AEO format
│   └── resize_screenshots.py  # Resize App Store screenshots for web
├── .github/workflows/
│   ├── pages.yml               # Deploy on push to main
│   └── publish.yml             # Cron Mon/Wed/Fri 9am UTC — generates new article
├── llms.txt                    # Content map for AI crawlers
├── robots.txt                  # With Sitemap directive
└── sitemap.xml                 # Full URL list with priority + changefreq
```

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
| Canonical link | Present with full URL |
| Meta description | Present with content |
| Article JSON-LD | `@type: Article` in `@graph` |
| FAQPage JSON-LD | `@type: FAQPage` with 5 Q&As |
| App Store link | Points to `jesus-says-now` |
| FAQ section | `<h2>Frequently Asked Questions</h2>` |
| Direct answer | First `<p>` is 10-80 words, answers immediately |

```bash
python3 scripts/check_aeo.py
# Expected: 21/21 pages pass AEO checks.
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
?utm_source=website&utm_medium=cta&utm_campaign=organic
```
For homepage: `utm_campaign=homepage-hero`
For download page: `utm_campaign=download-hero`

---

## Hermes Agent Loop

See `HERMES_AGENT.md` for the full daily/weekly agent playbook used by the automated publishing agent.
