# Competitor-Comparison SEO Pages Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Apply the PuffCount / Starter Story playbook to Jesus Says: validate demand through competitor and market research, inspect competitor features/onboarding/UI, then publish marketing-first comparison pages that position Jesus Says around real strengths.

**Architecture:** Keep the current static GitHub Pages site. Add comparison pages as `content/*.html` article pages using the existing `landing.css` chrome, JSON-LD, sitemap, `llms.txt`, and `content/queue.json` publishing workflow. Do not build a new CMS or app backend.

**Tech Stack:** Static HTML, existing Python article generators, existing AEO validator, GitHub Pages, public competitor research, App Store / website evidence.

---

## Why This Strategy Fits Jesus Says

The knowledge-base playbook says: market research first, competitor inspection second, marketing content third. Jesus Says already has the right foundation:

- `content/queue.json` controls the publishing queue.
- `scripts/generate_article.py` and `scripts/generate_article_api.py` generate AEO article pages.
- `scripts/check_aeo.py` validates article schema, direct answer format, FAQ, canonical URLs, and App Store CTAs.
- 24 current article pages already pass AEO validation.
- `sitemap.xml`, `llms.txt`, and `content/index.html` already support crawler discovery.

The missing wedge is comparison-intent SEO: people searching for alternatives to Hallow, Glorify, YouVersion, Abide, Bible Chat, and prayer apps are closer to app-install intent than generic “Bible verse” searchers.

---

## Current Baseline

Verified on 2026-05-08 from repo root `/Users/victor/github/jesussays-website`:

```bash
python3 scripts/check_aeo.py
# Expected/current: 24/24 pages pass AEO checks.
```

Live site checks returned HTTP 200 for:

```bash
curl -sI https://jesussays.app/
curl -sI https://jesussays.app/content/bible-verses-anxiety.html
```

---

## Constraints

- Do not change production HTML or scripts during the research/planning pass.
- Do not edit `index.html`, `download.html`, `assets/*.css`, `scripts/*.py`, `sitemap.xml`, `llms.txt`, or `content/queue.json` until implementation begins.
- Avoid unverified claims about competitors, theology, AI accuracy, pricing, or health outcomes.
- Use competitor names only for nominative comparison. Do not imply affiliation, endorsement, or certification.
- Keep pages helpful and fair, not attack pages.

---

## Target Files

### Create

- `docs/research/competitor-comparison-seo.md` — dated research notes and claims matrix.
- `content/best-christian-ai-prayer-apps.html`
- `content/jesus-says-vs-hallow.html`
- `content/jesus-says-vs-glorify.html`
- `content/jesus-says-vs-youversion.html`

### Modify Later

- `content/queue.json` — add comparison page queue entries.
- `content/index.html` — add “Compare Christian apps” or “App comparisons” section.
- `sitemap.xml` — include new comparison URLs.
- `llms.txt` — include new comparison pages for AI crawlers.

### Reuse

- `scripts/generate_article.py`
- `scripts/generate_article_api.py`
- `scripts/check_aeo.py`
- `assets/landing.css`

---

## Page Types

1. Best-of page
   - Example: `best-christian-ai-prayer-apps.html`
   - Intent: user is evaluating categories and wants options.
   - CTA: “Try Jesus Says if you want Scripture-grounded, personalized prayer reflection.”

2. Alternative page
   - Example: `jesus-says-vs-hallow.html`
   - Intent: user knows one large competitor and wants an alternative.
   - CTA: “Use Jesus Says for a lighter, conversation-style daily reflection companion.”

3. Use-case comparison
   - Example: `best-bible-chat-apps.html`
   - Intent: user wants interactive Bible or prayer conversation.
   - CTA: “Ask a personal faith question in Jesus Says.”

4. Switching page
   - Example: `hallow-alternative-for-daily-prayer.html`
   - Intent: user wants a specific competitor alternative for a specific use case.
   - Use after the first 4 pages show impressions.

---

## Initial Page Priorities

| Priority | File | Keyword | Type |
|---|---|---|---|
| P0 | `content/best-christian-ai-prayer-apps.html` | best Christian AI prayer app | Best-of |
| P0 | `content/jesus-says-vs-hallow.html` | Hallow alternative | Alternative |
| P0 | `content/jesus-says-vs-glorify.html` | Glorify alternative | Alternative |
| P0 | `content/jesus-says-vs-youversion.html` | YouVersion alternative | Alternative |
| P1 | `content/jesus-says-vs-abide.html` | Abide alternative | Alternative |
| P1 | `content/best-bible-chat-apps.html` | best Bible chat app | Best-of |
| P1 | `content/jesus-says-vs-bible-chat.html` | Bible Chat alternative | Alternative |
| P2 | `content/best-daily-devotional-apps.html` | best daily devotional app | Best-of |

---

## Research Checklist

For each competitor, document public evidence in `docs/research/competitor-comparison-seo.md`:

- App Store title, subtitle, screenshots, rating count, visible pricing/subscription notes, and observed date.
- Official website headline, positioning, features, onboarding language, and pricing language.
- SERP intent for each target keyword.
- Feature matrix:
  - prayer
  - Bible references
  - AI chat / conversation
  - devotionals
  - journaling
  - reminders/streaks
  - audio
  - community/church/small groups
  - platform support
- UI notes:
  - onboarding style
  - paywall timing
  - account requirement
  - trust/safety copy
  - pastoral/church boundary language
- Jesus Says proof points from:
  - `index.html`
  - `download.html`
  - `assets/screens/`
  - existing `content/*.html` pages

Mark every claim:

- `verified` — directly supported by public page or app metadata.
- `inferred` — likely, but avoid using in final page unless softened.
- `do not use` — unsupported, risky, or too negative.

---

## Compliance Guardrails

### Faith Claims

Use:

- “Scripture-grounded reflection”
- “prayer companion”
- “conversation-style guidance”
- “helps you reflect with Bible verses and prayer prompts”

Avoid:

- “Jesus literally answers you”
- “speaks for Jesus”
- “replaces church”
- “replaces pastors”
- “theologically perfect”
- “guaranteed biblical answer”

### AI Claims

Use:

- “AI-assisted”
- “personalized reflection”
- “conversation-style support”

Avoid:

- “hallucination-free”
- “most accurate AI Bible app”
- “God-powered AI”
- “divine answer”

### Mental Health / Crisis Claims

For anxiety, depression, grief, addiction, or crisis topics, include a clear boundary:

> Jesus Says is a prayer and Scripture reflection companion, not medical, mental health, legal, emergency, or pastoral care. If you may harm yourself or someone else, contact local emergency services or a crisis hotline immediately.

### Competitor Claims

Use practical tradeoffs:

- “Hallow is known for audio prayer and meditation; Jesus Says is better suited if you want short, text-based, personalized Scripture reflection.”

Avoid attack language:

- “Hallow is too expensive.”
- “Glorify is worse.”
- “YouVersion is outdated.”

---

## Page Requirements

Each page must follow the existing AEO article standard:

- Static `content/*.html` page.
- `<link rel="stylesheet" href="/assets/landing.css" />`
- Canonical: `https://jesussays.app/content/<slug>.html`
- 10-80 word direct-answer first paragraph.
- `Article` JSON-LD.
- `FAQPage` JSON-LD with 5 Q&As.
- Breadcrumb JSON-LD.
- App Store CTA to `jesus-says-now`.
- UTM format: `utm_campaign=content-<slug>`.
- “Companion, not replacement” footer/boundary language preserved.

---

## Initial Queue Additions

Add only after research is complete and claims are vetted:

```json
{"keyword":"best Christian AI prayer app","slug":"best-christian-ai-prayer-apps","status":"pending","type":"comparison","source":"competitor-research-2026-05"}
{"keyword":"Hallow alternative","slug":"jesus-says-vs-hallow","status":"pending","type":"comparison","source":"competitor-research-2026-05"}
{"keyword":"Glorify alternative","slug":"jesus-says-vs-glorify","status":"pending","type":"comparison","source":"competitor-research-2026-05"}
{"keyword":"YouVersion alternative","slug":"jesus-says-vs-youversion","status":"pending","type":"comparison","source":"competitor-research-2026-05"}
```

---

## Implementation Tasks

### Task 1: Create Competitor Research Doc

**Objective:** Establish a source-of-truth claims matrix before any comparison page is written.

**Files:**

- Create: `docs/research/competitor-comparison-seo.md`

**Steps:**

1. Create `docs/research/` if missing.
2. Add a table for Hallow, Glorify, YouVersion, Abide, Bible Chat, Pray.com.
3. Record public source URLs and observed date.
4. Add a “usable claims” column and a “do not use” column.
5. Commit:

```bash
git add docs/research/competitor-comparison-seo.md
git commit -m "docs: add competitor comparison SEO research matrix"
```

---

### Task 2: Add Comparison Queue Entries

**Objective:** Add first four comparison pages to the existing publishing queue.

**Files:**

- Modify: `content/queue.json`

**Steps:**

1. Insert P0 comparison entries after the already published items and before general pending items.
2. Validate JSON:

```bash
python3 -m json.tool content/queue.json >/tmp/queue.validated.json
```

3. Commit:

```bash
git add content/queue.json
git commit -m "content: add competitor comparison SEO queue entries"
```

---

### Task 3: Generate First Comparison Page

**Objective:** Generate `best-christian-ai-prayer-apps.html` using the existing article generator, then manually edit for competitor-claim safety.

**Files:**

- Create: `content/best-christian-ai-prayer-apps.html`
- Modify: `content/queue.json`
- Modify: `sitemap.xml`
- Modify: `llms.txt`

**Steps:**

1. Run:

```bash
python3 scripts/generate_article.py
```

2. Read the generated page and remove/soften any unsupported competitor claims.
3. Ensure direct answer is comparison-specific, not generic devotional content.
4. Run:

```bash
python3 scripts/check_aeo.py
```

5. Commit:

```bash
git add content/ sitemap.xml llms.txt
git commit -m "content: publish best Christian AI prayer apps comparison"
```

---

### Task 4: Generate Three Alternative Pages

**Objective:** Publish Hallow, Glorify, and YouVersion comparison pages with fair positioning.

**Files:**

- Create: `content/jesus-says-vs-hallow.html`
- Create: `content/jesus-says-vs-glorify.html`
- Create: `content/jesus-says-vs-youversion.html`
- Modify: `content/queue.json`
- Modify: `sitemap.xml`
- Modify: `llms.txt`

**Steps:**

1. Generate one page at a time:

```bash
python3 scripts/generate_article.py
python3 scripts/check_aeo.py
```

2. After each page, inspect for overclaims:

```bash
rg -n "cures|guaranteed|replaces church|replaces pastoral care|speaks for Jesus|most accurate|better than|worse than" content/jesus-says-vs-*.html content/best-christian-ai-prayer-apps.html
```

3. Edit manually if needed.
4. Commit each page separately.

---

### Task 5: Add Comparison Section to Library Index

**Objective:** Make comparison pages discoverable from the Faith Library.

**Files:**

- Modify: `content/index.html`

**Steps:**

1. Add a new section titled `Compare Christian apps`.
2. Link to the four new pages.
3. Keep the section visually consistent with existing `.lib-section` markup.
4. Validate no existing links broke.
5. Commit:

```bash
git add content/index.html
git commit -m "content: add Christian app comparisons to library"
```

---

### Task 6: Deploy and Verify

**Objective:** Push only after all local validations pass.

**Commands:**

```bash
git status --short
python3 scripts/check_aeo.py
python3 -m json.tool content/queue.json >/tmp/queue.validated.json
python3 -c "from xml.etree import ElementTree as ET; ET.parse('sitemap.xml'); print('sitemap ok')"
git push
```

After deploy:

```bash
curl -sI https://jesussays.app/content/best-christian-ai-prayer-apps.html
curl -sI https://jesussays.app/content/jesus-says-vs-hallow.html
curl -sI https://jesussays.app/content/jesus-says-vs-glorify.html
curl -sI https://jesussays.app/content/jesus-says-vs-youversion.html
```

Expected: HTTP 200 after GitHub Pages deploy finishes.

---

## 2-Week Sprint

### Week 1

- Day 1: Create competitor research doc and gather live App Store/site notes.
- Day 2: Build feature matrix and mark claims as verified, inferred, or do not use.
- Day 3: Validate SERP intent and choose first 4 pages.
- Day 4: Draft briefs: title, meta, direct answer, table rows, CTA, FAQ, guardrails.
- Day 5: Add first 4 queue items and generate draft pages.

### Week 2

- Day 6: Edit pages for clarity, source-date language, and compliance.
- Day 7: Run validation and fix AEO/JSON-LD/claim issues.
- Day 8: Update `content/index.html`, `sitemap.xml`, and `llms.txt`.
- Day 9: Deploy through GitHub Pages and verify live URLs.
- Day 10: Track Search Console impressions, CTR, average position, and App Store CTA clicks.

---

## Success Criteria

- 4 comparison pages live and passing `scripts/check_aeo.py`.
- Every competitor claim has dated research support.
- No faith, AI, health, or trademark overclaims.
- Each page has a canonical URL, FAQ schema, and App Store CTA.
- `content/index.html`, `sitemap.xml`, and `llms.txt` include the new URLs.
- Expansion to P1/P2 pages depends on 14 days of impressions, CTR, average position, and app CTA clicks.

---

## Recommendation

Yes, use this strategy — but start with comparison pages only after research, not pure AI-generated competitor pages. The wedge is strong because Jesus Says has a distinct positioning: lightweight, personalized, Scripture-grounded reflection rather than broad Bible app, audio meditation library, or generic AI chat.
