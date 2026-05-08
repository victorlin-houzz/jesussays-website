# Jesus Says Website — SEO/AEO Content Site Design

**Date:** 2026-05-08
**Project:** /Users/victor/github/jesussays-website
**Goal:** Route organic Christian search traffic to the Jesus Says iOS app via an AEO-optimized static content site published continuously on GitHub Pages.

---

## 1. Current State

- 22 static HTML content pages
- GitHub Pages via GHA (`pages.yml`), deploys on push to `main`
- Hosted at `https://victorlin-houzz.github.io/jesussays-website/`
- Gaps: inconsistent AEO structure across pages, placeholder App Store link, no continuous publishing pipeline

---

## 2. Architecture

**Stack (unchanged):** Plain HTML/CSS → GitHub Pages → GHA deploy.

**New components:**

| Component | Path | Purpose |
|---|---|---|
| Publish workflow | `.github/workflows/publish.yml` | Cron 3x/week, runs article generator |
| Article generator | `scripts/generate_article.py` | Anthropic SDK → AEO HTML → commit |
| Keyword queue | `content/queue.json` | Ordered list of topics for the agent |
| Article template | `scripts/template.html` | Canonical AEO structure |

**Deployment flow:**
```
publish.yml cron trigger
  → generate_article.py picks next queued keyword
  → calls Claude API with AEO article prompt
  → writes content/<slug>.html
  → updates sitemap.xml + llms.txt
  → marks keyword as published in queue.json
  → git commit + push → pages.yml deploys
```

---

## 3. AEO Article Template

Every page (new and upgraded) follows this structure. Each H2 must stand alone as a complete answer — AI models chunk content into self-contained blocks before citing.

```
<title>[Keyword]: [N] [Scripture/Steps/Answers] — Jesus Says [YEAR]</title>
<meta description> — 150-160 chars answering the question directly
<h1> — same as title minus year
<p> — Direct answer, 40-60 words (first paragraph, no preamble)
<h2> What does the Bible say about [topic]?
  → Numbered verse list, 1-sentence application each
<h2> How to [pray/apply/practice] when [situation]
  → 3-5 numbered steps
<h2> [Specific follow-on question]
  → 40-60 word atomic answer block
<section class="faq">
  <h2> Frequently Asked Questions
  → 4-6 Q&A pairs (FAQ schema targets)
<section class="cta">
  → App CTA with App Store link
JSON-LD: Article + FAQPage + BreadcrumbList
```

---

## 4. Content Strategy — Keyword Queue (Phase 1, 30 articles)

### Cluster A: Bible Verse for Specific Situation
- bible verses for anxiety about money
- bible verses for job loss and unemployment
- bible verses for loneliness and isolation
- bible verses for going through divorce
- bible verses for chronic illness and suffering
- bible verses for infertility and loss
- bible verses for grief and losing a parent

### Cluster B: Prayer for Specific Need
- short prayer for a friend with cancer
- prayer before surgery for peace
- prayer for financial breakthrough
- prayer for clarity in a difficult decision
- bedtime prayer for children with anxiety
- prayer for someone with addiction

### Cluster C: Daily Devotional by Audience
- daily devotional for new moms
- morning devotional for men in recovery
- daily devotional for single women trusting God
- devotional for teens with anxiety
- daily devotional for grief

### Cluster D: What Does the Bible Say About...
- what does the Bible say about depression
- what does the Bible say about comparison and envy
- what does the Bible say about social media
- what does the Bible say about debt and money
- what does the Bible say about digital rest and Sabbath

### Cluster E: Christian Advice (Trending 2025-26)
- Christian advice for setting dating boundaries
- Christian mindfulness vs secular mindfulness
- Christian advice for digital burnout and screen time
- what the Bible says about loneliness in marriage
- how to pray for a prodigal child
- Christian grief counseling — what Scripture says

---

## 5. One-Time Site Quality Upgrades

1. **All 22 existing pages:** Add FAQPage schema, AEO direct-answer paragraph (first 50 words), `<meta name="keywords">`, consistent breadcrumb
2. **Homepage (index.html):** Richer keyword cluster navigation by category; real App Store link
3. **CSS (assets/site.css):** Readability pass — font-size 18px body, line-height 1.7, max-width 680px, mobile padding
4. **llms.txt:** Expand to describe all content categories, keyword intent, and conversion goal
5. **sitemap.xml:** Add `<priority>` and `<changefreq>` per page
6. **robots.txt:** Add `Sitemap:` directive

---

## 6. Generate Script — `scripts/generate_article.py`

```
inputs:
  - ANTHROPIC_API_KEY (from env / GHA secret)
  - content/queue.json (reads next unpublished keyword)

outputs:
  - content/<slug>.html (AEO article)
  - updated sitemap.xml (new URL added)
  - updated llms.txt (new page listed)
  - updated queue.json (keyword marked published)

Claude prompt contract:
  - model: claude-opus-4-7 (highest quality for content)
  - system: SEO/AEO content writer persona
  - user: keyword + template spec + word count target (800-1200 words)
  - output: raw HTML block (no markdown wrapper)
```

---

## 7. GitHub Actions — `.github/workflows/publish.yml`

```yaml
schedule: "0 9 * * 1,3,5"  # Mon, Wed, Fri at 9am UTC
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
steps:
  - checkout (with write token for push)
  - install anthropic SDK
  - run generate_article.py
  - git add + commit + push
```

The existing `pages.yml` workflow handles deployment automatically on push.

---

## 8. App Store Link

Bundle ID: `com.jesussays.jesussays`
App Store URL: **TBD** — user must provide the numeric App Store ID.
Placeholder used across all pages: `https://apps.apple.com/app/jesus-says/id[APP_ID]`

---

## 9. Success Criteria

- 30 new AEO-optimized articles published within 10 weeks (automated)
- All 22 existing pages upgraded to AEO template
- Site indexed by Google Search Console (submit sitemap)
- AI citation: at least one page cited by ChatGPT/Perplexity for a target keyword within 60 days
- App installs routed from website (trackable via UTM parameter on App Store link)

---

## 10. Out of Scope

- Custom domain (can be added later via CNAME)
- Database or CMS backend
- User accounts or comments
- Monetization (ads, newsletter)
- Android app link (iOS only for now)
