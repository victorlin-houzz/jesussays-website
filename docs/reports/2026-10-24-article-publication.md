# Reviewed article publication

Scope approved in chat: publish the useful submitted topics and merge overlapping material, retaining the Faith Library's established style.

- Improve five existing guides with selected prayer, memorization, stress, Monday, and spiritual-growth material.
- Add three original guides, one new article per PR: quiet time (combines two submissions), prayer for a husband, and family morning prayer.
- Retain shared generated chrome, exact KJV quotations, contextual primary sources, sensitive-topic care notes, and current canonical URLs.
- Hold the books and Lauds submissions because their promised material is missing; do not open competing anxiety, beginner-prayer, stress, or growth-list pages.
- Verify build, AEO/editorial checks, Scripture source availability, metadata and links, and mobile/desktop rendering before opening reviewed PRs.

## Disposition of the submitted drafts

| Submitted topic | Result |
| --- | --- |
| Catholic Morning Prayer / Lauds | Held: no daily text/audio service; liturgical review needed. |
| Prayers for My Husband | Rewritten as `prayer-for-husband-during-hard-times`, with an early prayer, contextual verses, practical support, and safety boundaries. |
| Christian Books for Spiritual Growth | Held: no actual book recommendations; requires original research. |
| Prayer and Spiritual Growth / 30-Day Plan | Useful prayer themes merged into `7-day-devotional-for-new-faith`; no fixed growth deadline or invented biblical stages. |
| 16 Spiritual Growth Quotes | Consolidated with the growth themes; no competing list page or mixed-translation quotations. |
| Monday Morning Prayer | Focused Monday section merged into `morning-prayer-for-protection`; no weekday keyword pages. |
| Morning Prayer for Family | Rewritten as `morning-prayer-for-family`, with voluntary participation and adaptations for different households. |
| How to Pray Step by Step | Optional ACTS outline merged into `how-to-pray-according-to-the-bible`. |
| Quiet Time With God | Combined with the quiet-time verses submission into `quiet-time-with-god`. |
| Quiet-Time Bible Verses | Integrated as contextual Scripture anchors within the single quiet-time guide. |
| Scripture for Stress | Work-pressure table merged into `christian-advice-for-anxiety-at-work`; practical response guidance added to `bible-verses-anxiety`. Existing money and night-prayer guides retain their distinct jobs. |
| Bible Verse for Anxiety | Corrected, modest memorization guidance merged into `bible-verses-anxiety`; no second anxiety URL. |

## Editorial and presentation review

The new articles were written as original Jesus Says guides rather than copying the submitted outlines. The existing `build_site.py` renderer supplies the same navigation, typography, prayer and verse styling, byline, standard app CTA, related links, footer, canonical metadata, and Article structured data. No CSS or legal content changed. Optional FAQs were omitted where the body already answered the useful questions.

Independent editorial review found no blockers in the five substantive guide updates, the three new bodies, or each new article's final catalog and generated-page integration. New Scripture quotations were checked against `/Users/victor/github/quotebible/assets/bible/kjv.json`, including inline quotations; primary-source links returned HTTP 200. New descriptions are 140–160 characters and SEO titles are at most 60 characters. All new pages have one prayer block and a 40–60-word direct answer.

Contextual links were added from the daily devotional to the quiet-time guide, the family/marriage guide to the husband prayer, and the morning-protection guide to the family morning prayer. No existing URLs were removed or redirected.

## Verification

- `python3 scripts/build_site.py` passed before each publication PR.
- `KJV_BIBLE_PATH=/Users/victor/github/quotebible/assets/bible/kjv.json python3 scripts/check_aeo.py` passed at each step: 37, 38, 39, and finally 40 articles, with 305 redirect stubs. Quote verification was enabled, not silently skipped for the isolated worktree.
- `python3 scripts/site_analytics.py --check` passed, finally covering 354 pages.
- `git diff --check` passed.
- Browser checks passed at 390 × 900 and 1440 × 900 for every changed article: no page overflow, one H1, correct canonical, shared CSS, valid JSON-LD, working mobile menu, loaded screenshots, and resolving legal links. Screenshots were visually inspected.
- Still Waters Add ink, palette selection, pause/resume, drift toggle, wash, and keyboard ink controls passed at both widths.
- Initial browser checking flagged an offscreen lazy-loaded image before scrolling. Waiting for the image to enter the viewport and decode confirmed it loads; no production change was needed.

## Publication route

Each new article uses a separate PR to main, following the repository's one-article-per-PR policy. Existing guide improvements were published in [PR #14](https://github.com/victorlin-houzz/jesussays-website/pull/14), quiet time in [PR #15](https://github.com/victorlin-houzz/jesussays-website/pull/15), and the husband prayer in [PR #16](https://github.com/victorlin-houzz/jesussays-website/pull/16). This report accompanies the final family-prayer PR.

The historical opportunity tracker was preserved: 104 skipped, 228 merged, 11 published, and 157 retired entries. Its historical published count is not the live catalog count. No existing tracker status was reset, and no bulk generator was run.
