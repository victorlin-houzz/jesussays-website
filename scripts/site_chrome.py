"""Shared page chrome for jesussays.app: head, nav, mobile menu, footer and App Store links.

Every page on the site (landing, library, articles, Still Waters, About, Download, 404)
renders its navigation and footer from this module so the site stays visually and
structurally consistent. `scripts/build_site.py` applies it; the article generator
imports it for new drafts.
"""
from __future__ import annotations

import html
import json

SITE = "https://jesussays.app"
APP_ID = "6756906208"
APP_NAME = "Jesus Says: Daily Reflection"
APP_STORE_URL = f"https://apps.apple.com/us/app/jesus-says-daily-reflection/id{APP_ID}"
OG_IMAGE = f"{SITE}/assets/og-image.png"
CONTACT_EMAIL = "jesussays889@gmail.com"
ORG_ID = f"{SITE}/#organization"
# Profiles the company runs (listed in HERMES_AGENT.md). Organization.sameAs and the footer use these.
X_URL = "https://x.com/JesusSaysNow"
TIKTOK_URL = "https://www.tiktok.com/@jesus.says.now889"
INSTAGRAM_URL = "https://www.instagram.com/jesus.says.now/"
SAME_AS = [APP_STORE_URL, X_URL, INSTAGRAM_URL, TIKTOK_URL]
AUTHOR_PATH = "/author/jesus-says-team/"
WEBSITE_ID = f"{SITE}/#website"

APPLE_SVG = (
    '<svg class="apple" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35'
    "-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 "
    "3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.08l.01-.01zM12 7.25c-.15-2.23 1.66-4.07 "
    '3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>'
)

BRAND_MARK = """<span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 22V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C9 11 7 9 7 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C15 11 17 9 17 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </span>"""

# (label, href on the homepage, href everywhere else, key used for aria-current)
NAV_ITEMS = [
    ("Features", "#features", "/#features", "features"),
    ("A Daily Practice", "#day", "/#day", "day"),
    ("App Tour", "#screens", "/#screens", "screens"),
    ("Still Waters", "/play/still-waters/", "/play/still-waters/", "still-waters"),
    ("Faith Library", "/content/", "/content/", "library"),
    ("FAQ", "#faq", "/#faq", "faq"),
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def app_store_url(campaign: str, source: str = "website", medium: str = "cta") -> str:
    """App Store link with UTM tags (kept for referrer analysis on our side)."""
    return f"{APP_STORE_URL}?utm_source={source}&amp;utm_medium={medium}&amp;utm_campaign={campaign}"


def app_store_button(campaign: str, extra_class: str = "") -> str:
    cls = f"btn-apple {extra_class}".strip()
    return (
        f'<a class="{cls}" href="{app_store_url(campaign)}" rel="nofollow">\n'
        f"        {APPLE_SVG}\n"
        '        <span class="stack"><small>Download on the</small><span>App Store</span></span>\n'
        "      </a>"
    )


def _links(home: bool, current: str | None, indent: str) -> str:
    out = []
    for label, home_href, href, key in NAV_ITEMS:
        target = home_href if home else href
        cur = ' aria-current="page"' if key == current else ""
        out.append(f'{indent}<a href="{target}"{cur}>{label}</a>')
    return "\n".join(out)


def nav_html(home: bool = False, current: str | None = None, campaign_prefix: str = "") -> str:
    """Skip link, mobile menu overlay and the sticky pill navigation."""
    prefix = f"{campaign_prefix}-" if campaign_prefix else ""
    small_apple = APPLE_SVG.replace('class="apple"', 'width="16" height="16"')
    nav_apple = APPLE_SVG.replace(' class="apple"', "")
    return f"""<!-- site:nav -->
<a class="skip-link" href="#main">Skip to content</a>
<div class="mobile-menu" id="mobile-menu" role="dialog" aria-modal="true" aria-label="Navigation menu" hidden>
{_links(home, current, "  ")}
  <a class="mm-cta" href="{app_store_url(prefix + 'mobile-menu')}" rel="nofollow">
    {small_apple}
    Get the App
  </a>
</div>
<div class="nav-wrap">
  <nav class="nav" aria-label="Primary">
    <a href="/" class="brand" aria-label="Jesus Says — Home">
      {BRAND_MARK}
      <span class="brand-name">Jesus Says</span>
    </a>
    <div class="nav-links">
{_links(home, current, "      ")}
    </div>
    <a class="nav-cta" href="{app_store_url(prefix + 'nav')}" rel="nofollow">
      {nav_apple}
      Get the App
    </a>
    <button class="nav-burger" id="nav-burger" aria-label="Open navigation menu" aria-expanded="false" aria-controls="mobile-menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
  </nav>
</div>
<!-- /site:nav -->"""


def footer_html(home: bool = False, campaign_prefix: str = "") -> str:
    prefix = f"{campaign_prefix}-" if campaign_prefix else ""
    base = "" if home else "/"
    return f"""<!-- site:footer -->
<footer class="site">
  <div>
    <div class="brand footer-brand">
      {BRAND_MARK}
      <span class="brand-name">Jesus Says</span>
    </div>
    <p class="meta">A daily Scripture reflection and prayer app for iPhone and iPad. A companion for prayer, not a replacement for church, pastoral care, or professional help.</p>
  </div>
  <div>
    <h2 class="footer-h">App</h2>
    <ul>
      <li><a href="{base}#features">Features</a></li>
      <li><a href="{base}#screens">App Tour</a></li>
      <li><a href="/play/still-waters/">Still Waters</a></li>
      <li><a href="{app_store_url(prefix + 'footer')}" rel="nofollow">Download on the App Store</a></li>
    </ul>
  </div>
  <div>
    <h2 class="footer-h">Faith Library</h2>
    <ul>
      <li><a href="/content/bible-verses-anxiety.html">Bible verses for anxiety</a></li>
      <li><a href="/content/how-to-pray-according-to-the-bible.html">How to pray</a></li>
      <li><a href="/content/daily-devotional-today.html">A devotional for today</a></li>
      <li><a href="/content/">All articles</a></li>
    </ul>
  </div>
  <div>
    <h2 class="footer-h">Jesus Says</h2>
    <ul>
      <li><a href="/about.html">About &amp; editorial standards</a></li>
      <li><a href="/download.html">About the app</a></li>
      <li><a href="{base}#faq">FAQ</a></li>
      <li><a href="{AUTHOR_PATH}">Who writes the guides</a></li>
      <li><a href="mailto:{CONTACT_EMAIL}">Contact</a></li>
      <li><a href="{X_URL}" rel="me">Jesus Says on X</a></li>
      <li><a href="{INSTAGRAM_URL}" rel="me">Jesus Says on Instagram</a></li>
      <li><a href="{TIKTOK_URL}" rel="me">Jesus Says on TikTok</a></li>
    </ul>
  </div>
  <div class="legal">
    <span>© 2026 Jesus Says</span>
    <span class="links">
      <a href="/privacy_policy.html">Privacy Policy</a>
      <a href="/terms_of_use.html">Terms of Use</a>
      <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
    </span>
  </div>
</footer>
<!-- /site:footer -->"""


def head_html(
    *,
    title: str,
    description: str,
    canonical: str,
    og_type: str = "website",
    robots: str = "index, follow, max-image-preview:large",
    json_ld: list[dict] | None = None,
    extra: str = "",
) -> str:
    """Everything inside <head>. `title` is the full <title> text."""
    ld = ""
    if json_ld:
        graph = {"@context": "https://schema.org", "@graph": json_ld}
        ld = '\n  <script type="application/ld+json">\n' + json.dumps(graph, ensure_ascii=False, indent=2) + "\n  </script>"
    return f"""  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{canonical}" />
  <meta name="robots" content="{robots}" />
  <meta name="apple-itunes-app" content="app-id={APP_ID}" />
  <meta name="theme-color" content="#EFE9DC" />
  <meta property="og:site_name" content="Jesus Says" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{OG_IMAGE}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />
  <meta name="twitter:image" content="{OG_IMAGE}" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="/assets/landing.css" />{extra}{ld}"""


def organization_node() -> dict:
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": "Jesus Says",
        "url": f"{SITE}/",
        "logo": OG_IMAGE,
        "email": CONTACT_EMAIL,
        "sameAs": SAME_AS,
    }


def website_node() -> dict:
    return {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "name": "Jesus Says",
        "url": f"{SITE}/",
        "publisher": {"@id": ORG_ID},
        "inLanguage": "en-US",
    }


def breadcrumb_node(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": url}
            for i, (name, url) in enumerate(items, start=1)
        ],
    }


SCRIPTS = '<script src="/assets/nav.js" defer></script>'
