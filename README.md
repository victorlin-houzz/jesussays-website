# Jesus Says — website

Static site on GitHub Pages for the iPhone and iPad app **Jesus Says: Daily Reflection**
([App Store](https://apps.apple.com/us/app/jesus-says-daily-reflection/id6756906208)). Its job is to help people
find the app: an honest landing page, a small Faith Library of Scripture-based guides, and Still Waters, a quiet
moment from the app that runs in the browser.

- **Live site:** https://jesussays.app
- **Privacy Policy:** https://jesussays.app/privacy_policy.html
- **Terms of Use:** https://jesussays.app/terms_of_use.html

Use these URLs in App Store Connect and all app marketing. Do not point new legal links to victorlin.us.
After approving legal changes in the app repository, run `python3 scripts/sync_legal.py ../quotebible`
(requires Pandoc), review the Markdown/HTML diff, and publish through a PR. This keeps the in-app documents and
public pages aligned without inventing policy wording during a site update.

Promotion copy follows `../quotebible/Documentation/APP_STORE_LISTING.md`. Never describe the app as AI-powered,
an AI chat, or with clinical/wellness words (see `../quotebible/AGENTS.md`), and don't claim reflections stay on
the device.

## Layout

```
index.html                 Landing page (hand-authored; nav/footer injected by the build)
download.html, about.html  About the app; About & editorial standards
404.html                   Friendly not-found page (GitHub Pages serves it for missing URLs)
play/still-waters/         Still Waters in the browser (WebGL renderer from the app, MIT attribution kept)
content/<slug>.html        Faith Library articles (generated chrome + hand/AI-edited body)
content/index.html         Faith Library index (generated)
content/queue.json         Keyword backlog for new articles ("pending", "covered", "published", "skipped")
content/opportunities.jsonl  Competitor research backlog (ideas only, not a publishing queue)
_data/library.json         Catalog of live articles: the single source of truth
_data/redirects.json       Retired article URL -> live article (redirect stubs are generated)
assets/landing.css         The one stylesheet for every page
assets/nav.js              Shared mobile menu and anchor scrolling
sitemap.xml, llms.txt      Generated from the catalog
_config.yml                Keeps docs/, scripts/, and other internal files off the public site
docs/editorial-guidelines.md  How Faith Library articles are written and checked
```

## Building and checking

```bash
python3 scripts/build_site.py   # re-render articles, library, sitemap, llms.txt, redirect stubs, shared nav/footer
python3 scripts/check_aeo.py    # structure, metadata, verbatim-KJV quotes, care notes, duplicates, registration
python3 -m http.server 8411     # preview at http://localhost:8411
```

`build_site.py` owns everything outside the `<!-- article:body -->` markers in an article and everything between
the `<!-- site:nav -->` / `<!-- site:footer -->` markers on hand-authored pages. Edit article bodies and
`_data/library.json`; don't hand-edit generated chrome.

The KJV check reads the app's bundled Bible at `../quotebible/assets/bible/kjv.json` (override with
`KJV_BIBLE_PATH`). Look up exact verse text with `python3 scripts/kjv.py "Psalm 46:10"`.

## Faith Library

The library is deliberately small. In September 2026 it was consolidated from ~520 pages (most of them
keyword-swapped template clones) to 37 guides; see `docs/reports/2026-09-28-site-audit.md`. Rules:

- One strong page per real question. Improve an existing article before adding a near-duplicate.
- Every page must be registered in `_data/library.json`. `check_aeo.py` fails on any unregistered file in
  `content/`, which is what keeps templated pages from creeping back.
- Scripture is quoted from the KJV, word for word, to match the app's reader.
- Sensitive topics carry care notes (988, domestic violence and SAMHSA lines where relevant).
- Retiring or merging a page: remove it from the catalog, add `old-slug: target-slug` to `_data/redirects.json`
  (or delete the file if nothing fits), then build.

### Adding an article

1. Pick a keyword from `content/queue.json` that no live article already answers.
2. Draft it: `python3 scripts/generate_article.py` (local `claude` CLI) or `--backend api`
   (`ANTHROPIC_API_KEY`). The draft is checked against `docs/editorial-guidelines.md`, sent back for repairs if it
   fails, then added to the catalog and rendered. Or write the body by hand and add a catalog entry.
3. Read the whole article. Run `build_site.py` and `check_aeo.py`, preview on mobile and desktop.
4. Open a PR to `main`. Merging deploys.

The **Draft Faith Library Article** workflow (`.github/workflows/publish.yml`) does steps 1–2 in GitHub Actions
and opens a PR; it runs only when started by hand. It needs the `ANTHROPIC_API_KEY` secret and an `ARTICLES_PAT`
with access to this repo and `victorlin-houzz/quotebible` (for the KJV file).

## App Store links

All App Store links come from `scripts/site_chrome.py` and point to
`https://apps.apple.com/us/app/jesus-says-daily-reflection/id6756906208` with `utm_*` tags
(`utm_campaign=content-<slug>`, `home-hero`, `nav`, `footer`, `still-waters-after`, ...). Apple's App Analytics
ignores `utm_*`; to see campaign installs in App Store Connect, add `pt=<provider token>&ct=<campaign>` to the
link builder. Every page also carries the Smart App Banner (`<meta name="apple-itunes-app">`).

## Screenshots

The 2.0 screenshot inventory and original checksums are in `docs/screenshots-2.0.json`. Web images are in
`assets/screens/2.0/`; full-resolution Apple upload files are preserved in `~/Desktop/JesusSays-2.0-AppStore/`
(seven iPhone 6.9-inch images and six iPad 13-inch images). Do not upscale web images for Apple uploads.

## Deploying

Pushing to `main` deploys. GitHub Pages currently builds the branch with Jekyll ("legacy" build), and
`.github/workflows/pages.yml` also deploys a Jekyll build of the same branch; both honour `_config.yml`.
Pick one: switching Pages to "GitHub Actions" in repository settings makes `pages.yml` the only deployer.
