# Jesus Says website

- `https://jesussays.app/` is the canonical promotion site.
- Permanent legal URLs are `https://jesussays.app/privacy_policy.html` and `https://jesussays.app/terms_of_use.html`. Never publish new app links to victorlin.us.
- Keep the approved legal Markdown and rendered HTML here in sync with `../quotebible/assets/`. Do not silently rewrite legal terms during a marketing update. Use `python3 scripts/sync_legal.py ../quotebible` after approved app legal changes.
- Update App Store Connect privacy URL, marketing URL, and description Terms of Use link to the canonical URLs whenever preparing a release. Do not submit a version for review unless the user requests submission.
- Use screenshots of the actual current app. Record version, source commit, dimensions and checksums in `docs/screenshots-<version>.json`. Keep full-resolution Apple upload originals outside temporary storage.
- Keep promotion copy consistent with `../quotebible/Documentation/APP_STORE_LISTING.md`. Do not claim reflections never leave the device or promise unreleased features.
- Use `assets/landing.css`; preserve the existing article publishing workflow.
- Verify changed pages on mobile and desktop, legal links, screenshot loading, and playable preview controls before publishing via a PR to main.
