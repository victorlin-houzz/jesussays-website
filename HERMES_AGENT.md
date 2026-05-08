# Hermes Agent — Jesus Says Daily Publishing Loop

This document is the complete playbook for the Hermes automated agent. Run it as a daily cron job. It operates the Jesus Says content machine end-to-end: article generation, queue maintenance, keyword research, and cross-platform content output.

**Mission:** Maximize organic traffic from Google/AI search → Jesus Says Now iOS app installs → paywall conversion.

**Channels:**
- Site: https://victorlin-houzz.github.io/jesussays-website/
- App: https://apps.apple.com/us/app/jesus-says-now/id6756906208
- X: https://x.com/JesusSaysNow
- TikTok: https://www.tiktok.com/@jesus.says.now889

---

## Agent Context

- Working directory: `/Users/victor/github/jesussays-website` (or wherever the repo is cloned)
- Tools available: Bash, Read, Write, Edit, WebSearch, WebFetch
- The site is static HTML deployed via GitHub Pages on push to `main`
- Article generator: `scripts/generate_article.py` (uses `claude` CLI, no API key) or `scripts/generate_article_api.py` (uses `ANTHROPIC_API_KEY`)
- AEO validator: `scripts/check_aeo.py`
- Keyword queue: `content/queue.json`

---

## Daily Loop (run every day)

### Phase 1: Generate Today's Article

```bash
cd /path/to/jesussays-website
python3 scripts/generate_article.py
```

If the queue is exhausted, move to Phase 3 (keyword research) immediately.

After generating:
```bash
python3 scripts/check_aeo.py
```

If the new article FAILS validation:
1. Read the generated file to diagnose which check failed
2. Rewrite the failing section (most common: direct answer too short, missing FAQ h2)
3. Re-run `check_aeo.py` until PASS
4. Commit:
   ```bash
   git add content/ sitemap.xml llms.txt content/queue.json
   git commit -m "content: publish $(date +%Y-%m-%d) — [keyword]"
   git push
   ```

### Phase 2: Generate Cross-Platform Content

After each new article, output the following (write to a file `content/social/YYYY-MM-DD.md`):

**X/Twitter Thread:**
```
Tweet 1 (hook — pick ONE format):
  - Contrarian: "Everyone says [X]. Here's what Jesus actually said."
  - Foreshadowing: "This [verse/prayer] changed my week — here's exactly what it was."
  - Question: "Has [situation from article keyword] happened to you? Jesus addressed it directly."

Tweet 2-4: Pull 3 Bible verses from the article. Format each:
  "[Reference]: '[Verse text]'"
  One-sentence application.

Tweet 5: CTA reply (post as reply to thread, not main tweet):
  "If this helped, the Jesus Says Now app gives you personalized Scripture for your exact moment.
  Download free: https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=x&utm_medium=thread&utm_campaign=[slug]"
```

**TikTok Concept:**
```
Format: Fact slideshow (5 slides)
Hook (slide 1): "[Emotional hook related to keyword]"
Slides 2-5: One verse per slide — "Book Chapter:Verse — verse text"
Audio: Use currently trending Christian/inspirational audio
CTA overlay on slide 5: "Get more at JesusSays app ↓"
Caption: "[Hook repeated]. #JesusSaysNow #BibleVerse #[topic] #Christian #Faith"
```

### Phase 3: Queue Maintenance (run when queue has < 10 pending items)

Search Google Trends and web for current high-volume Christian search queries. Add 10 new keywords to the front of `content/queue.json`:

**Research prompt to run:**
Search for:
1. "google trends bible verse 2025 2026"
2. "most searched Christian questions [current year]"
3. "trending faith topics [current month]"

**Keyword criteria to add:**
- Must be a specific situation, not a broad term ("bible verse when your parent is sick" not "bible verses")
- Prefer "what would Jesus say about X" format (near-zero competition, high AI citation rate)
- Prefer "is it a sin to X" format (AEO gold — these get pulled into AI Overviews)
- Prefer "how do Christians deal with X" format (3,000-4,000 monthly searches, low competition)

**Add to queue.json** (prepend before existing pending items):
```json
{"keyword": "[new keyword]", "slug": "[kebab-case-slug]", "status": "pending", "volume_est": [estimated monthly searches], "source": "research-[YYYY-MM]"}
```

### Phase 4: Homepage Refresh (run weekly, every Monday)

Update the homepage to highlight the week's most recent articles:

1. Read `content/queue.json` — find the 3 most recently published articles
2. Add them to the relevant category section in `index.html`
3. Commit: `git commit -m "content: homepage refresh with latest articles"`

---

## Weekly Deep Loop (run every Sunday)

### Keyword Performance Review

Search for newly trending Christian keywords:
```
Search: "trending bible searches [month] [year]"
Search: "most googled faith questions [year]"
Search: "Christian mental health topics [year]"
Search: "new bible verse trends google trends"
```

Evaluate against what's already published — if a topic is already covered, skip it. Add only net-new keyword opportunities.

### AEO Audit

Run the validator to confirm all pages still pass:
```bash
python3 scripts/check_aeo.py
```

If any pages FAIL (e.g., after a template update), re-run upgrade on those pages:
```bash
ANTHROPIC_API_KEY=... python3 scripts/upgrade_pages.py content/<failing-page>.html
```

### Social Media Recap Post

Every Sunday, write a recap X thread:
```
Tweet 1: "This week Jesus Says published [N] new Scripture guides. The most shared:"
Tweet 2-4: Link to each article with its hook quote
Tweet 5 (reply): App CTA
```

---

## Monthly Strategy Loop (run on the 1st of each month)

### 1. Reorder Queue by Volume

Sort all `"pending"` items in `queue.json` by `volume_est` descending (highest traffic opportunity first). Items without `volume_est` go to the end.

### 2. Content Gap Analysis

Search for:
- Which Christian content categories have the most searches but fewest results on the site?
- What "what would Jesus say about X" topics haven't been covered?
- What AEO "is it a sin to X" topics haven't been covered?

Add 20 new keywords based on findings.

### 3. Existing Article Refresh

Pick the 3 oldest published articles. Re-run the upgrade script on them to refresh content, update `datePublished` in schema, and re-validate. Commit with: `git commit -m "content: refresh 3 older articles for freshness"`

### 4. Sitemap Lastmod Update

Update `<lastmod>` dates in `sitemap.xml` for all refreshed articles to today's date. This signals freshness to Google.

---

## Content Formats by Goal

| Goal | Best Content Format | CTA |
|---|---|---|
| App installs | "What would Jesus say about X" (interactive hook) | "Get your personalized answer in the app" |
| App installs | "Prayer for X" (in-the-moment need) | "Find more prayers in the Jesus Says app" |
| Paywall conversion | Confession prayer sequences | "Access full confession prayer journal in app" |
| Paywall conversion | Daily devotional series | "Continue your daily habit in the app" |
| X traffic | Contrarian verse threads | Link to full article |
| TikTok traffic | Fact slideshow + trending audio | "Download Jesus Says" CTA overlay |

---

## Paywall Conversion Content Rules

When writing articles that specifically target paywall conversion, emphasize:

1. **Interactive value** — "The Jesus Says app gives you a *personalized* response to your exact prayer, not a generic verse list."
2. **Habit framing** — "Download Jesus Says to build a daily faith practice" (not "get content")
3. **Completion moments** — CTA goes immediately after the most emotionally resonant section (after the FAQ, after confession prayer steps)
4. **Social proof hook** — "Thousands of Christians use Jesus Says daily for..."
5. **Free trial framing** — Emphasize "free to download" in every CTA

---

## App Store UTM Parameters

Always use UTM tracking on App Store links:

| Source | Campaign |
|---|---|
| Article body | `utm_campaign=organic` |
| Homepage hero | `utm_campaign=homepage-hero` |
| Homepage screenshots | `utm_campaign=homepage-screenshots` |
| Download page | `utm_campaign=download-hero` |
| X thread reply | `utm_campaign=x-thread` |
| TikTok bio | `utm_campaign=tiktok-bio` |

Full format: `https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=[source]&utm_medium=cta&utm_campaign=[campaign]`

---

## Error Recovery

| Problem | Recovery |
|---|---|
| Generator fails (claude CLI not found) | Use `generate_article_api.py` with `ANTHROPIC_API_KEY` |
| AEO check fails on new article | Read file, fix the specific failing check, re-run validator |
| Queue empty | Run Phase 3 keyword research immediately |
| Git push fails (conflict) | `git pull --rebase origin main && git push` |
| `sitemap.xml` malformed | Validate with `python3 -c "from xml.etree import ElementTree as ET; ET.parse('sitemap.xml')"` |

---

## Quality Standards

Every published article must:
- Pass `python3 scripts/check_aeo.py` (all 8 AEO checks)
- Have 800-1000 words of body content
- Include 4-6 Bible verses with specific references and applications
- Include exactly 5 FAQ Q&A pairs
- Use `<nav>` (not `<p>`) for the back-link to preserve direct-answer detection
- Have the App Store CTA with `rel="nofollow"` and UTM parameters

---

## Daily Commit Convention

```
content: publish YYYY-MM-DD — [keyword]        # new article
content: add N keywords to queue               # queue expansion
content: refresh [page] for freshness          # article update
content: homepage refresh with latest articles # homepage update
seo: update sitemap lastmod                    # sitemap maintenance
```
