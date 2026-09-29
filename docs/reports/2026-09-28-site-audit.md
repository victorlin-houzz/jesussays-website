# jesussays.app audit and consolidation — 2026-09-28

Goal: promote **Jesus Says: Daily Reflection** (App Store id6756906208) with a site that search engines, answer
engines, and people trust, so it no longer reads like a content farm.

## What the audit found

### 1. Scaled, templated content (critical)
- `content/` held **522 articles**. Through May 10 the site had 28 reviewed pages. From May 23 to June 7 the nightly
  opportunity pipeline added about 50 pages a night.
- **473 of 522 pages** had under 10% unique 8-word phrases: the same ~760-word template with a keyword pasted in,
  e.g. `what-would-jesus-say-about-acts`, `when-you-feel-rosary-bible-help-for-today`,
  `confession-prayer-for-love`. They attached the same five *anxiety* verses to Acts, Rosary, Baptism, and Lent.
  They came from the `--local-only` fallback of `generate_opportunity_articles.py`.
- This is the pattern Google's scaled-content-abuse policy targets. Site-wide it drags down the pages that are
  good, and it makes the site look like spam to anyone who browses the library.

### 2. Accuracy and positioning
- The homepage FAQ said voice reflections are "immediately discarded" and that data stays "only on your device by
  default". The Privacy Policy says reflection text goes to our servers and to Google Gemini, and that transcripts
  are kept on the device for Mercy Timeline. It also gave a menu path ("Settings → Data") that doesn't exist.
- Site copy promised features that aren't in the approved 2.0 listing ("confession journaling", "personalized
  Bible verses", "Talk to Jesus", "streaks", "smart reminders"). The comparison pages sold the app as
  "AI-personalized" and "AI prayer app", which the app's positioning rules forbid.
- Articles quoted modern translations (mostly NIV wording) with no attribution. The app and homepage use the KJV.
- Every App Store link used the old `jesus-says-now` slug, and the schema named the app "Jesus Says Now".

### 3. SEO / AEO plumbing
- The sitemap listed 529 URLs, 473 of them thin. `llms.txt` was a 559-line dump of those pages.
- The deploy published the whole repository: `HERMES_AGENT.md` ("Maximize organic traffic → … paywall
  conversion"), competitor research, `content/queue.json`, and a public `keyword-clusters.html` SEO roadmap were
  all live on jesussays.app.
- There was no custom 404, no Smart App Banner, no FAQPage schema for the homepage FAQ, and no structured data or
  social meta on Still Waters. Article pages had no related-article links.
- The scheduled "Publish New Article" workflow had failed three times a week since July (missing `ARTICLES_PAT`).
  If it had worked, it would have pushed unreviewed articles to `main`.

### 4. Style consistency
- Articles used 8 different inline `<style>` blocks and 2 footer variants. The About page had no site navigation
  at all. Nav links differed across page types. A legacy `site.css` and 1.x screenshots were still in the repo.
- On a 375px phone the nav's menu button overflowed the viewport on every page except Still Waters. The closed
  mobile menu stayed keyboard-focusable, because `display: flex` overrode `hidden`.

### 5. Still Waters as a promotion
- The game page had no App Store call-to-action beyond the nav, no way into the app's other Be Still moments,
  and no social or structured-data metadata. Articles never linked to it.

## What changed

**Library: 522 → 37 articles.**
- 12 overlapping pages were merged into their strongest sibling, e.g. three "purpose" pages became one.
  `best-christian-ai-prayer-apps` was renamed `best-christian-prayer-apps`.
- 305 retired URLs redirect (meta refresh + canonical + noindex) to the live article on the same topic.
- 182 pages on topics with no live article (Acts, Rosary, Holy Week, Lent, etc.) were deleted. They now hit a
  helpful `404.html`.
- All 37 articles were rewritten (978–1,545 words, median 1,320). Each has a direct-answer opening,
  question-style headings, and 4–6 real FAQs.
- Every Scripture quote is verbatim KJV, checked against the app's bundled Bible, and verses are read in context.
- Care notes (988, the domestic violence hotline, SAMHSA) appear where the topic calls for them. App pitches
  inside article bodies were removed; one standard, honest CTA per page does that job.
- Comparison pages were re-verified against competitors' official pages (Sept 2026). They say plainly where
  another app is the better fit.

**Structure and tooling**
- `_data/library.json` is now the single catalog. `scripts/build_site.py` renders every article's chrome,
  JSON-LD (Article, FAQPage from the visible FAQ, BreadcrumbList), the library index, sitemap, llms.txt, redirect
  stubs, and the shared nav/footer on hand-authored pages.
- `scripts/check_aeo.py` and `scripts/content_rules.py` now fail on:
  - non-KJV quotes;
  - banned positioning wording;
  - missing care notes;
  - near-duplicate text across articles;
  - any `content/` file not registered in the catalog or redirect map.
- `scripts/generate_article.py` drafts one article at a time, based on `docs/editorial-guidelines.md`. It repairs
  failures with exact KJV text, then leaves the draft for PR review. The publish workflow is manual-only and
  opens a PR.
- Retired: the batch opportunity generator and its audit script, the one-shot migration and upgrade scripts, the
  old API generator, `site.css`, 1.x screenshots, and `keyword-clusters.html`.

**Pages**
- Homepage:
  - accurate privacy FAQ and feature copy that matches the listing;
  - new FAQs on who writes reflections and on Still Waters;
  - FAQPage and MobileApplication JSON-LD;
  - topic-based library block.
- Still Waters:
  - a "three quiet moments" app section with an App Store CTA and screenshots of Peace, Be Still and Consider the
    Heavens;
  - a gentle in-game prompt after about 40 seconds or 6 touches;
  - reading links, WebApplication JSON-LD, and OG/Twitter meta;
  - the shared nav script (CSP-compatible).
- Every article ends with a Still Waters card.
- About now covers editorial standards, and Download is rebuilt from the listing. A 404 page was added.
- Every page gets the Smart App Banner, favicon, skip link, shared `assets/nav.js`, and `assets/landing.css`.
- `_config.yml` keeps docs, scripts, data, and agent playbooks off the public site. `pages.yml` builds with
  Jekyll so both deploy paths produce the same output.

## Owner follow-ups (not done here)

1. **App Store listing:**
   - The live page is still **v1.5.4** (May 24), while the site describes 2.0 (Be Still, 7-day path, typing).
     Ship 2.0 or hold the site PR until it's live.
   - The live description publicly shows an internal note: "Coming after Share Cards ship; do not submit this
     screenshot until the feature is released."
   - The listing shows a **Plus Plan Weekly** ($4.99) purchase the approved listing doesn't mention, and a
     **"Contains Advertising"** label. Please check both in App Store Connect.
2. **GitHub Pages settings:**
   - Turn on **Enforce HTTPS** (currently off).
   - Verify the custom domain (currently "unverified").
   - Choose one deploy source (switching to "GitHub Actions" makes `pages.yml` the only deployer).
3. **Search Console:** submit the new sitemap. Use the Removals tool only if you want the deleted URLs gone faster.
   Watch coverage: redirected URLs should drop out over the next few weeks.
4. **App Analytics:** App Store Connect ignores `utm_*`. Add your provider token (`pt`) and campaign (`ct`) to
   `app_store_url()` in `scripts/site_chrome.py` to measure installs per page.
5. **Review choices:**
   - the About page's disclosure that guides are written "sometimes with the help of AI writing tools";
   - Catholic-practice wording in the confession, prayer, and marriage guides;
   - named recovery groups;
   - the relationships page's line on sexual ethics;
   - the daily devotional showing the same passage every day.
6. **Secrets:** the draft workflow needs `ANTHROPIC_API_KEY` and an `ARTICLES_PAT` that can read
   `victorlin-houzz/quotebible`.

## How to verify

```bash
python3 scripts/build_site.py && python3 scripts/check_aeo.py   # 37 articles, 305 redirect stubs, all PASS
python3 -m http.server 8411                                       # spot-check pages on mobile and desktop
```

After deploy:
- `https://jesussays.app/HERMES_AGENT.md` and `https://jesussays.app/content/queue.json` should return 404.
- `https://jesussays.app/content/daily-devotional-on-anxiety.html` should land on the anxiety guide.
