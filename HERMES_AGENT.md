# Hermes Agent — Jesus Says content playbook

This playbook is for the automated Hermes agent that helps maintain jesussays.app and its social channels.

**Mission:** help people find the iPhone and iPad app **Jesus Says: Daily Reflection** by keeping a small,
trustworthy Faith Library, promoting Still Waters, and turning existing articles into social posts. Quality over
volume, always.

**Hard rules**
- Never publish directly to `main`. Every site change goes through a pull request that a person merges.
- Never add more than **one** new article per week, and only for a question no live article already answers.
- Never create pages by swapping keywords into a template. In 2026 this produced ~470 spam-like pages that had to
  be deleted (see `docs/reports/2026-09-28-site-audit.md`).
- Follow `docs/editorial-guidelines.md`: KJV quotes word for word, care notes on sensitive topics, no
  "AI-powered"/chat/clinical/wellness framing of the app, no claims that reflections stay on the device.
- `python3 scripts/build_site.py && python3 scripts/check_aeo.py` must pass before a PR is opened.

**Channels**
- Site: https://jesussays.app
- App: https://apps.apple.com/us/app/jesus-says-daily-reflection/id6756906208
- X: https://x.com/JesusSaysNow
- TikTok: https://www.tiktok.com/@jesus.says.now889

---

## Weekly (Monday)

1. **Health check.** Run `python3 scripts/check_aeo.py`. If anything fails, open a PR that fixes it (or report it)
   before doing anything else.
2. **At most one new article.** Choose the highest-value `pending` keyword in `content/queue.json` that no live
   article covers (check `_data/library.json`). Run `python3 scripts/generate_article.py`, read the result in full,
   fix anything that reads as generic, and open a PR titled `content: draft <title>`. If no keyword clearly earns a
   page, skip the week.
3. **Social posts from existing articles** (write to `content/social/YYYY-MM-DD.md`, not published by the site):
   - X thread: a hook, 3 verses from the article (exact KJV text with references) with one-line applications, and
     a reply linking the article. App link, if used:
     `https://apps.apple.com/us/app/jesus-says-daily-reflection/id6756906208?utm_source=x&utm_medium=thread&utm_campaign=<slug>`
   - TikTok slideshow: hook slide, 3–4 verse slides, final slide "Two quiet minutes with God — Jesus Says".
   - Once a month, a Still Waters post linking https://jesussays.app/play/still-waters/.
   Describe the app only with features from `../quotebible/Documentation/APP_STORE_LISTING.md`.

## Monthly (1st)

1. **Refresh one article.** Pick the article with the oldest `modified` date in `_data/library.json`. Re-read it
   against the guidelines, improve it where it's weak, update `modified`, rebuild, and open a PR.
2. **Queue review.** Mark keywords that an existing article already answers as `"status": "covered"` with
   `"covered_by": "<slug>"`. Add at most five new, specific keywords (a real situation, not a broad term) with
   `"status": "pending"` and a `"source"` note.
3. **Comparison pages.** Re-check competitor facts on `best-christian-prayer-apps` and the three
   `jesus-says-vs-*` pages against official sources; update the "Details checked" line.

## Never

- Bulk-generate, bulk-refresh, or bump `modified` dates without real changes.
- Add pages outside `_data/library.json`, or link to retired URLs (the build fails if you do).
- Edit legal pages (use `scripts/sync_legal.py` after the app repo's legal text is approved).
- Submit anything to App Store Connect.

## Error recovery

| Problem | Recovery |
|---|---|
| `generate_article.py` can't find the KJV Bible | Clone `quotebible` next to this repo or set `KJV_BIBLE_PATH` |
| Draft fails review after repairs | Don't force it. Write or edit the body by hand, or skip the keyword |
| `check_aeo.py` reports an unregistered page | Add it to `_data/library.json` or `_data/redirects.json`, or delete it |
| Git push rejected | `git pull --rebase origin main`, rebuild, re-run checks, push the branch again |
