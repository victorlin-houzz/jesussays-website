# Jesus Says website

- `https://jesussays.app/` is the canonical promotion site.
- Permanent legal URLs are `https://jesussays.app/privacy_policy.html` and `https://jesussays.app/terms_of_use.html`. Never publish new app links to victorlin.us.
- Keep the approved legal Markdown and rendered HTML here in sync with `../quotebible/assets/`. Do not silently rewrite legal terms during a marketing update. Use `python3 scripts/sync_legal.py ../quotebible` after approved app legal changes.
- Update App Store Connect privacy URL, marketing URL, and description Terms of Use link to the canonical URLs whenever preparing a release. Do not submit a version for review unless the user requests submission.
- Use screenshots of the actual current app. Record version, source commit, dimensions and checksums in `docs/screenshots-<version>.json`. Keep full-resolution Apple upload originals outside temporary storage.
- Keep promotion copy consistent with `../quotebible/Documentation/APP_STORE_LISTING.md`. Do not claim reflections never leave the device or promise unreleased features. Link the App Store as `https://apps.apple.com/us/app/jesus-says-daily-reflection/id6756906208` (via `scripts/site_chrome.py`).
- Use `assets/landing.css`. Faith Library articles are registered in `_data/library.json` and rendered by `python3 scripts/build_site.py`; edit article bodies and the catalog, not generated chrome. New articles follow `docs/editorial-guidelines.md` (verbatim KJV, care notes, one page per real question) and ship one at a time through a reviewed PR. Never bulk-generate templated pages.
- Run `python3 scripts/build_site.py && python3 scripts/check_aeo.py` before every PR; both must pass.
- Verify changed pages on mobile and desktop, legal links, screenshot loading, and playable preview controls before publishing via a PR to main.
