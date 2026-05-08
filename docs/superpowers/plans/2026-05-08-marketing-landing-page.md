# Jesus Says Marketing Landing Page — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plain-HTML SEO content hub at `index.html` with a high-fidelity marketing landing page that mirrors the Jesus Says iOS app's visual identity, while preserving all existing `/content/*.html` SEO URLs.

**Architecture:** Single static HTML page with separate `assets/landing.css` (isolated from article-page `assets/site.css`). Self-hosted Merriweather + Lato fonts in `assets/fonts/`. Compressed WebP + PNG screenshots in `assets/screens/`. No JS framework — one inline `<script>` block handles mobile menu + smooth scroll.

**Tech Stack:** Vanilla HTML5, CSS3 (custom properties, Grid, Flexbox), WebP/PNG `<picture>` elements, self-hosted Google Fonts woff2, GitHub Pages.

---

## Source of truth

Before any task, read both files:
- `design_handoff_jesussays_website/README.md` — design tokens, section specs, link wiring
- `design_handoff_jesussays_website/Jesus Says - Website.html` — complete reference HTML+CSS (1094 lines)

The CSS is in `<style>` lines 11–626. The HTML body starts at line 629. All image paths in the reference use `site-assets/` prefix — update every one to `/assets/screens/` in the output.

Canonical domain: `jesussays.app` (per `CNAME`). App Store ID: `id6756906208`.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `assets/screens/*.png` | Resized (880px wide) PNG fallbacks |
| Create | `assets/screens/*.webp` | WebP primary images (<200KB each) |
| Create | `assets/fonts/*.woff2` | Self-hosted Lato + Merriweather latin subset |
| Create | `assets/landing.css` | All landing-page CSS (tokens, nav, hero, all sections, responsive, mobile menu) |
| Replace | `index.html` | New marketing landing page (all 10 sections) |

Do **not** modify: `assets/site.css`, `content/*.html`, `download.html`, `sitemap.xml`.

---

### Task 1: Process and copy screenshots

**Files:**
- Create: `assets/screens/` directory
- Create: `assets/screens/*.png` (resized, 880px wide)
- Create: `assets/screens/*.webp` (WebP at quality 82)

- [ ] **Step 1: Create output directory**

```bash
mkdir -p assets/screens
```

- [ ] **Step 2: Resize PNGs to 880px wide using sips (macOS built-in)**

```bash
cd /Users/victor/github/jesussays-website
for f in bible chat devotion-paths home journal reflection result welcome; do
  echo "Resizing $f.png..."
  sips -Z 880 "design_handoff_jesussays_website/site-assets/${f}.png" \
    --out "assets/screens/${f}.png"
done
```

Expected: 8 PNG files in `assets/screens/`. Run `ls -lh assets/screens/*.png` to verify.

- [ ] **Step 3: Create WebP versions using ffmpeg**

```bash
for f in bible chat devotion-paths home journal reflection result welcome; do
  echo "Creating $f.webp..."
  ffmpeg -y -i "assets/screens/${f}.png" \
    -vcodec libwebp -quality 82 \
    "assets/screens/${f}.webp" 2>/dev/null
done
```

- [ ] **Step 4: Verify file sizes**

```bash
ls -lh assets/screens/
```

Expected: WebP files should all be under 200KB. PNG files may be larger (WebP is the primary served format). If any WebP is still over 200KB, rerun with `-quality 70`.

- [ ] **Step 5: Commit**

```bash
git add assets/screens/
git commit -m "feat: add compressed + WebP screenshot set for landing page"
```

---

### Task 2: Self-host Google Fonts (Lato + Merriweather)

**Files:**
- Create: `assets/fonts/lato-400.woff2`
- Create: `assets/fonts/lato-600.woff2`
- Create: `assets/fonts/lato-700.woff2`
- Create: `assets/fonts/merriweather-400.woff2`
- Create: `assets/fonts/merriweather-400-italic.woff2`
- Create: `assets/fonts/merriweather-700.woff2`

- [ ] **Step 1: Create fonts directory**

```bash
mkdir -p assets/fonts
```

- [ ] **Step 2: Download font woff2 files via Python script**

Save the following as `/tmp/download_fonts.py` and run it from the repo root:

```python
#!/usr/bin/env python3
import re, subprocess, os

os.makedirs('assets/fonts', exist_ok=True)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
gfonts_url = (
    "https://fonts.googleapis.com/css2"
    "?family=Lato:wght@400;600;700"
    "&family=Merriweather:ital,wght@0,400;0,700;1,400"
    "&display=swap"
)

result = subprocess.run(
    ['curl', '-s', gfonts_url, '-H', f'User-Agent: {UA}'],
    capture_output=True, text=True
)
css = result.stdout

blocks = re.findall(r'@font-face \{([^}]+)\}', css, re.DOTALL)
seen = set()

for block in blocks:
    family = re.search(r"font-family: '([^']+)'", block)
    weight = re.search(r'font-weight: (\d+)', block)
    style  = re.search(r'font-style: (\w+)', block)
    url_m  = re.search(r"url\((https://fonts\.gstatic\.com[^)]+\.woff2)\)", block)
    urange = re.search(r'unicode-range: ([^\n;]+)', block)

    if not (family and weight and style and url_m):
        continue
    # Only download the latin subset (U+0000-00FF marks the latin block)
    if urange and 'U+0000-00FF' not in urange.group(1):
        continue

    fname = f"{family.group(1).lower().replace(' ', '-')}-{weight.group(1)}"
    if style.group(1) == 'italic':
        fname += '-italic'
    fname += '.woff2'

    if fname in seen:
        continue
    seen.add(fname)

    print(f"Downloading {fname} ...")
    subprocess.run(['curl', '-s', url_m.group(1), '-o', f'assets/fonts/{fname}'])
    print(f"  -> assets/fonts/{fname}")

print("Done.")
```

Run it:

```bash
python3 /tmp/download_fonts.py
```

Expected output:
```
Downloading lato-400.woff2 ...
  -> assets/fonts/lato-400.woff2
Downloading lato-600.woff2 ...
  -> assets/fonts/lato-600.woff2
Downloading lato-700.woff2 ...
  -> assets/fonts/lato-700.woff2
Downloading merriweather-400.woff2 ...
  -> assets/fonts/merriweather-400.woff2
Downloading merriweather-700.woff2 ...
  -> assets/fonts/merriweather-700.woff2
Downloading merriweather-400-italic.woff2 ...
  -> assets/fonts/merriweather-400-italic.woff2
Done.
```

- [ ] **Step 3: Verify all 6 files downloaded**

```bash
ls -lh assets/fonts/
```

Expected: 6 `.woff2` files, each 20-60KB. If any is missing or 0 bytes, check your internet connection and rerun.

- [ ] **Step 4: Commit**

```bash
git add assets/fonts/
git commit -m "feat: self-host Lato + Merriweather woff2 (latin subset)"
```

---

### Task 3: Create assets/landing.css

**Files:**
- Create: `assets/landing.css`

This CSS file has three parts:
1. `@font-face` declarations (replaces the Google Fonts `<link>`)
2. All design CSS from `design_handoff_jesussays_website/Jesus Says - Website.html` lines 11–626 (the `<style>` block content), verbatim except: remove the Google Fonts `@import`; the `<style>` wrapper is dropped since this is an external file
3. Mobile menu additions (new, not in the design reference)

- [ ] **Step 1: Create the file with @font-face declarations at the top**

Create `assets/landing.css` with the following content at the top (font-face block), then append the rest:

```css
/* ─── SELF-HOSTED FONTS ─────────────────────────────────── */
@font-face {
  font-family: 'Lato';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/assets/fonts/lato-400.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0300-0302, U+0304, U+0308, U+0323, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Lato';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('/assets/fonts/lato-600.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0300-0302, U+0304, U+0308, U+0323, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Lato';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('/assets/fonts/lato-700.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0300-0302, U+0304, U+0308, U+0323, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Merriweather';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/assets/fonts/merriweather-400.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0300-0302, U+0304, U+0308, U+0323, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Merriweather';
  font-style: italic;
  font-weight: 400;
  font-display: swap;
  src: url('/assets/fonts/merriweather-400-italic.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0300-0302, U+0304, U+0308, U+0323, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Merriweather';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('/assets/fonts/merriweather-700.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0300-0302, U+0304, U+0308, U+0323, U+0329, U+2000-206F, U+20AC, U+2122, U+2215, U+FEFF, U+FFFD;
}
```

- [ ] **Step 2: Append all CSS from the design reference (lines 12–625)**

Open `design_handoff_jesussays_website/Jesus Says - Website.html`. Copy the entire content of the `<style>` block (everything between `<style>` and `</style>` on lines 11–626). Append it to `assets/landing.css`.

The design reference already includes `:root` variables, all component styles, and `@media` queries. Do not alter any values — copy verbatim.

- [ ] **Step 3: Append mobile menu CSS**

Append the following block at the end of `assets/landing.css`:

```css
/* ─── MOBILE MENU ───────────────────────────────────────── */
.mobile-menu {
  position: fixed; top: 0; left: 0; right: 0; z-index: 49;
  padding: 80px 20px 28px;
  background: rgba(251, 247, 236, 0.97);
  -webkit-backdrop-filter: saturate(140%) blur(18px);
  backdrop-filter: saturate(140%) blur(18px);
  border-bottom: 1px solid var(--line);
  box-shadow: 0 14px 40px -22px rgba(26,31,74,0.30);
  transform: translateY(-110%);
  transition: transform .28s cubic-bezier(.4,0,.2,1);
  display: flex; flex-direction: column; gap: 6px;
}
.mobile-menu.open {
  transform: translateY(0);
}
.mobile-menu a {
  padding: 14px 18px; border-radius: 14px; font-size: 18px;
  font-weight: 600; color: var(--ink-soft);
  font-family: var(--sans);
  transition: background .15s, color .15s;
}
.mobile-menu a:hover, .mobile-menu a:focus {
  background: rgba(26,31,74,0.06); color: var(--ink);
  outline: none;
}
.mobile-menu .mm-cta {
  margin-top: 10px;
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--ink); color: #fff;
  padding: 14px 22px; border-radius: 999px;
  font-size: 16px; font-weight: 600;
  width: fit-content;
}
.mobile-menu .mm-cta:hover { background: var(--ink-2); color: #fff; }
body.menu-open { overflow: hidden; }
@media (min-width: 981px) { .mobile-menu { display: none; } }
```

- [ ] **Step 4: Commit**

```bash
git add assets/landing.css
git commit -m "feat: add landing.css with design tokens, all section styles, mobile menu"
```

---

### Task 4: Create index.html — head + nav + hero

**Files:**
- Replace: `index.html`

- [ ] **Step 1: Write the full HTML head**

Replace `index.html` entirely with the following (this is the opening, continue adding below in later steps):

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Jesus Says — Faith answers for real life. Free on iPhone.</title>
  <meta name="description" content="Receive Scripture for your exact moment. Talk to Jesus by voice. Build a daily faith rhythm with devotionals, prayer, and reflection. Free on iPhone." />
  <meta name="keywords" content="jesus says app, bible app, daily devotional, prayer app, christian app, bible verses, faith app" />
  <link rel="canonical" href="https://jesussays.app/" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:title" content="Jesus Says — Faith answers for real life." />
  <meta property="og:description" content="Receive Scripture for your exact moment. Talk to Jesus by voice. Build a daily faith rhythm. Free on iPhone." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://jesussays.app/" />
  <meta property="og:image" content="https://jesussays.app/assets/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Jesus Says — Faith answers for real life." />
  <meta name="twitter:description" content="Receive Scripture for your exact moment. Talk to Jesus by voice. Free on iPhone." />
  <link rel="stylesheet" href="/assets/landing.css" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "MobileApplication",
    "name": "Jesus Says Now",
    "operatingSystem": "iOS",
    "applicationCategory": "LifestyleApplication",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    "url": "https://apps.apple.com/us/app/jesus-says-now/id6756906208",
    "description": "Personalized Bible verses, voice prayer, confession journaling, and daily devotionals. Free on iPhone.",
    "screenshot": [
      "https://jesussays.app/assets/screens/home.png",
      "https://jesussays.app/assets/screens/reflection.png"
    ]
  }
  </script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Jesus Says",
    "url": "https://jesussays.app/",
    "description": "Christian content hub with Bible verses, prayer guides, daily devotionals, and faith-based advice."
  }
  </script>
</head>
<body>
```

- [ ] **Step 2: Add the mobile menu overlay (placed before nav-wrap)**

Append to `index.html`:

```html
<!-- Mobile menu overlay -->
<div class="mobile-menu" id="mobile-menu" role="dialog" aria-modal="true" aria-label="Navigation menu" hidden>
  <a href="#features">Features</a>
  <a href="#day">A Daily Practice</a>
  <a href="#screens">App Tour</a>
  <a href="#library">Faith Library</a>
  <a href="#faq">FAQ</a>
  <a class="mm-cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=mobile-menu" rel="nofollow">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.08l.01-.01zM12 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
    Get the App
  </a>
</div>
```

- [ ] **Step 3: Add nav HTML**

Append to `index.html` (copy from design reference lines 631–660, update App Store link with UTM):

```html
<!-- NAV -->
<div class="nav-wrap">
  <nav class="nav" aria-label="Primary">
    <a href="/" class="brand" aria-label="Jesus Says — Home">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 22V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C9 11 7 9 7 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C15 11 17 9 17 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </span>
      <span class="brand-name">Jesus Says</span>
    </a>
    <div class="nav-links" role="list">
      <a href="#features" role="listitem">Features</a>
      <a href="#day" role="listitem">A Daily Practice</a>
      <a href="#screens" role="listitem">App Tour</a>
      <a href="#library" role="listitem">Faith Library</a>
      <a href="#faq" role="listitem">FAQ</a>
    </div>
    <a class="nav-cta" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=nav" rel="nofollow">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.08l.01-.01zM12 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
      Get the App
    </a>
    <button class="nav-burger" id="nav-burger" aria-label="Open navigation menu" aria-expanded="false" aria-controls="mobile-menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
  </nav>
</div>
```

- [ ] **Step 4: Add hero section**

Append to `index.html` (copy from design reference lines 663–721, update image src and add `<picture>` wrapper):

```html
<!-- HERO -->
<header class="hero">
  <div>
    <span class="eyebrow"><span class="dot" aria-hidden="true"></span>Now on iPhone · Free</span>
    <h1>Faith answers, <em>for</em> <span class="glow">real life.</span></h1>
    <p class="lede">A daily companion for prayer, reflection, and scripture. Receive the verse for your exact moment. Talk to Jesus by voice. Build a quiet rhythm — one day at a time.</p>
    <div class="hero-ctas">
      <a class="btn-apple" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=home-hero" rel="nofollow">
        <svg class="apple" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.08l.01-.01zM12 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
        <span class="stack"><small>Download on the</small><span>App Store</span></span>
      </a>
      <a class="btn-ghost" href="#screens">
        <span class="play" aria-hidden="true"><svg viewBox="0 0 12 12" fill="currentColor"><path d="M2 1.5v9l8-4.5z"/></svg></span>
        See a 30-second tour
      </a>
    </div>
    <div class="trust">
      <span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z"/></svg>Private by default</span>
      <span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 13l4 4L19 7"/></svg>Free to download</span>
      <span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/></svg>iPhone · iOS 16+</span>
    </div>
  </div>
  <div class="phone-stage">
    <div class="phone-glow" aria-hidden="true"></div>
    <div class="phone" aria-hidden="true">
      <div class="notch"></div>
      <div class="screen">
        <picture>
          <source srcset="/assets/screens/home.webp" type="image/webp" />
          <img src="/assets/screens/home.png" alt="Jesus Says home screen showing Verse of the Day and daily rhythm" width="304" height="626" />
        </picture>
      </div>
    </div>
    <div class="float-card fc-1 gold" aria-hidden="true">
      <div class="ic">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/></svg>
      </div>
      <div><div class="t">Talk to Jesus</div><div class="s">90-second voice prayer</div></div>
    </div>
    <div class="float-card fc-2" aria-hidden="true">
      <div class="ic">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
      </div>
      <div><div class="t">Verse for this moment</div><div class="s">— Matthew 11:28</div></div>
    </div>
    <div class="float-card fc-3" aria-hidden="true">
      <div class="ic">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
      </div>
      <div><div class="t">3-minute reflection</div><div class="s">Begin your morning rhythm</div></div>
    </div>
  </div>
</header>
```

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: landing page head + nav + hero sections"
```

---

### Task 5: Add Quiet Band + Features sections

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Append quiet band section**

```html
<!-- QUIET BAND -->
<section class="quiet" aria-label="Scripture">
  <p class="verse"><span class="quote" aria-hidden="true">&ldquo;</span>Come unto me, all ye that labour and are heavy laden, and I will give you rest.<span class="quote" aria-hidden="true">&rdquo;</span></p>
  <p class="attr">Matthew 11:28</p>
</section>
```

- [ ] **Step 2: Append features section**

Copy the features section from the design reference (lines 730–845) verbatim, with one change: add `<main>` wrapping landmark around the features section and all sections below (close `</main>` before the footer). The features section has 7 article cards — copy all SVG icons exactly as written in the design reference.

The features section starts at line 730 of the design reference (`<!-- ──────────────── FEATURES ──────────────── -->`). Copy through line 845 (`</section>`).

Verify the resulting HTML includes:
- `<section class="block" id="features">` with `aria-labelledby` set (add `id="features-heading"` to the `<h2>`)
- All 7 `.feat` articles (`f1` through `f7`)
- The `.verse-mini` card inside `.f2`
- The `.chip-row` inside `.f6` and `.f7`
- The `.mic` and `.mic-stage` divs inside `.f1`

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: landing page quiet band + features bento grid"
```

---

### Task 6: Add Day Flow + Gallery sections

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Append "A Day with Jesus Says" section**

Copy from design reference lines 847–884, but replace every `src="site-assets/X.png"` with a `<picture>` element:

```html
<!-- Example replacement for each img inside .shot .frame .scr -->
<picture>
  <source srcset="/assets/screens/devotion-paths.webp" type="image/webp" />
  <img src="/assets/screens/devotion-paths.png" alt="Choose your journey — Foundations, Daily Strength, or Deep Study" />
</picture>
```

Apply the same `<picture>` pattern for `reflection.png` and `result.png`. Use descriptive alt text per the handoff spec:
- `devotion-paths.png` → `alt="Choose your journey — Foundations, Daily Strength, or Deep Study"`
- `reflection.png` → `alt="Personal reflection voice recording screen"`
- `result.png` → `alt="Reflection result with scripture and prayer"`

- [ ] **Step 2: Append gallery section**

Copy from design reference lines 886–909. Replace each `src="site-assets/X.png"` with a `<picture>` element using the same pattern. Apply to all 8 `.g-phone` items.

Image alt text map (use exact values):
- `welcome.png` → `alt="Jesus Says welcome screen"`
- `home.png` → `alt="Home screen — Verse of the Day and daily rhythm"`
- `devotion-paths.png` → `alt="Choose your devotion journey"`
- `reflection.png` → `alt="Personal reflection voice screen"`
- `result.png` → `alt="Reflection result with Scripture"`
- `bible.png` → `alt="Holy Bible reader — KJV"`
- `journal.png` → `alt="Personal journal — private and on-device"`
- `chat.png` → `alt="Talk to Jesus by voice"`

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: landing page day flow + gallery sections with WebP picture elements"
```

---

### Task 7: Add Faith Library + FAQ sections

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Append Faith Library section**

Copy from design reference lines 911–967, with these exact link corrections (use `/content/` prefix for all internal links):

```html
<!-- Bible verses column -->
<li><a href="/content/bible-verses-anxiety.html">For anxiety and worry</a></li>
<li><a href="/content/bible-verses-for-strength-hard-times.html">For strength in hard times</a></li>
<li><a href="/content/bible-verses-about-faith-and-trust.html">On faith and trust</a></li>
<li><a href="/content/bible-verses-about-peace-and-fear.html">On peace and fear</a></li>

<!-- Prayer guides column -->
<li><a href="/content/prayer-for-healing.html">A prayer for healing</a></li>
<li><a href="/content/morning-prayer-for-protection.html">Morning prayer for protection</a></li>
<li><a href="/content/night-prayer-for-sleep-and-anxiety.html">Night prayer for sleep</a></li>
<li><a href="/content/prayer-for-depression-and-hopelessness.html">Prayer for hopelessness</a></li>
<li><a href="/content/prayer-for-family-and-marriage.html">For family and marriage</a></li>

<!-- Confession + forgiveness column -->
<li><a href="/content/confession-prayer-guide.html">Confession guide (Psalm 51)</a></li>
<li><a href="/content/confession-prayer-after-failure.html">Confession after failure</a></li>
<li><a href="/content/confession-prayer-for-addiction-recovery.html">For addiction recovery</a></li>
<li><a href="/content/love-and-forgiveness.html">Love &amp; forgiveness in Scripture</a></li>

<!-- Daily devotionals column -->
<li><a href="/content/daily-devotional-today.html">A devotional for today</a></li>
<li><a href="/content/daily-devotional-on-financial-stress.html">For financial stress</a></li>
<li><a href="/content/daily-devotional-on-forgiveness.html">On forgiveness</a></li>
<li><a href="/content/daily-devotional-on-purpose.html">On purpose &amp; calling</a></li>
<li><a href="/content/christian-advice-for-relationships.html">Christian advice for relationships</a></li>

<!-- Browse CTA -->
<div class="lib-foot">
  <a href="/content/index.html">Browse the full library →</a>
</div>
```

- [ ] **Step 2: Append FAQ section**

Copy from design reference lines 969–1006 verbatim. Add `aria-expanded` and `id` attributes to each `<details>` summary for accessibility:

```html
<details class="faq-item" open id="faq-q1">
  <summary aria-expanded="true">Is Jesus Says free?</summary>
  <div class="ans"><p>Yes — the core experience is free, including the Bible, daily devotional, and your first voice reflection. A 7-day free trial unlocks unlimited reflections, full devotion journeys, and journal history. Cancel anytime.</p></div>
</details>
<details class="faq-item" id="faq-q2">
  <summary aria-expanded="false">Is my voice and journal private?</summary>
  <div class="ans"><p>Yes. Voice reflections are processed and immediately discarded — only the text response and your written notes persist, and only on your device by default. You can delete everything from Settings → Data.</p></div>
</details>
<details class="faq-item" id="faq-q3">
  <summary aria-expanded="false">Is this a replacement for church or a pastor?</summary>
  <div class="ans"><p>No. Jesus Says is a companion for prayer and Scripture in the in-between moments — not a substitute for community, communion, or pastoral care. It's a doorway back into Scripture, not a destination.</p></div>
</details>
<details class="faq-item" id="faq-q4">
  <summary aria-expanded="false">What translation of the Bible do you use?</summary>
  <div class="ans"><p>We currently use the King James Version (KJV) for the in-app reader. Additional translations are coming.</p></div>
</details>
<details class="faq-item" id="faq-q5">
  <summary aria-expanded="false">Will it work on Android?</summary>
  <div class="ans"><p>iPhone first. Android is on the roadmap — drop your email below and we'll let you know when it's ready.</p></div>
</details>
<details class="faq-item" id="faq-q6">
  <summary aria-expanded="false">How do I cancel my subscription?</summary>
  <div class="ans"><p>Through the App Store: <em>Settings → your name → Subscriptions → Jesus Says</em>. Apple handles billing — we never see your card.</p></div>
</details>
```

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: landing page faith library (SEO links) + FAQ accordion"
```

---

### Task 8: Add Final CTA + Footer + close tags

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Close `<main>` and append final CTA**

```html
</main>

<!-- FINAL CTA -->
<section class="final" aria-labelledby="final-heading">
  <div class="final-inner">
    <span class="star" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/></svg>
    </span>
    <h2 id="final-heading">Five minutes a day. <em style="font-style:italic; color: var(--gold-soft); font-weight:400;">A quieter year ahead.</em></h2>
    <p>Download Jesus Says today. Free on iPhone. No ads, no tracking, no shame loops — just Scripture and the small daily practice that builds a year.</p>
    <a class="btn-apple" href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=final" rel="nofollow">
      <svg class="apple" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.08l.01-.01zM12 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
      <span class="stack"><small>Download on the</small><span>App Store</span></span>
    </a>
    <small>iPhone · iOS 16+ · Free with optional 7-day trial</small>
  </div>
</section>
```

- [ ] **Step 2: Append footer**

```html
<!-- FOOTER -->
<footer class="site">
  <div>
    <div class="brand" style="margin-bottom: 14px;">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 22V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C9 11 7 9 7 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M12 11C15 11 17 9 17 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </span>
      <span class="brand-name">Jesus Says</span>
    </div>
    <p class="meta">A daily companion for prayer, reflection, and scripture. A companion, not a replacement for church or pastoral care.</p>
  </div>
  <div>
    <h5>App</h5>
    <ul>
      <li><a href="#features">Features</a></li>
      <li><a href="#day">Daily Practice</a></li>
      <li><a href="#screens">App Tour</a></li>
      <li><a href="https://apps.apple.com/us/app/jesus-says-now/id6756906208?utm_source=website&amp;utm_medium=cta&amp;utm_campaign=footer" rel="nofollow">Download</a></li>
    </ul>
  </div>
  <div>
    <h5>Library</h5>
    <ul>
      <li><a href="/content/bible-verses-anxiety.html">Verses for anxiety</a></li>
      <li><a href="/content/prayer-for-healing.html">Prayer for healing</a></li>
      <li><a href="/content/daily-devotional-today.html">Today's devotional</a></li>
      <li><a href="/content/index.html">All articles</a></li>
    </ul>
  </div>
  <div>
    <h5>Company</h5>
    <ul>
      <li><a href="#faq">FAQ</a></li>
      <li><a href="mailto:hello@jesussays.app">Contact</a></li>
      <li><a href="/download.html">About the App</a></li>
    </ul>
  </div>
  <div class="legal">
    <span>© 2026 Jesus Says</span>
    <span class="links">
      <a href="mailto:hello@jesussays.app">hello@jesussays.app</a>
    </span>
  </div>
</footer>
```

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: landing page final CTA + footer"
```

---

### Task 9: Add mobile menu JS + smooth scroll

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Append inline script before `</body>`**

Add the following complete `<script>` block just before `</body>`:

```html
<script>
(function() {
  // ── Smooth scroll with sticky-nav offset ──
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
      var id = a.getAttribute('href');
      if (id.length > 1) {
        var t = document.querySelector(id);
        if (t) {
          e.preventDefault();
          window.scrollTo({ top: t.getBoundingClientRect().top + window.scrollY - 90, behavior: 'smooth' });
        }
      }
    });
  });

  // ── Mobile menu ──
  var burger = document.getElementById('nav-burger');
  var menu   = document.getElementById('mobile-menu');
  var isOpen = false;

  function openMenu() {
    isOpen = true;
    menu.removeAttribute('hidden');
    // Trigger reflow so CSS transition fires
    menu.offsetHeight;
    menu.classList.add('open');
    burger.setAttribute('aria-expanded', 'true');
    burger.setAttribute('aria-label', 'Close navigation menu');
    document.body.classList.add('menu-open');

    // Update burger icon to X
    burger.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>';

    // Focus first menu item
    var firstLink = menu.querySelector('a');
    if (firstLink) firstLink.focus();
  }

  function closeMenu() {
    isOpen = false;
    menu.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'Open navigation menu');
    document.body.classList.remove('menu-open');

    // Restore burger icon
    burger.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';

    // Hide after transition (280ms)
    setTimeout(function() {
      if (!isOpen) menu.setAttribute('hidden', '');
    }, 300);

    burger.focus();
  }

  burger.addEventListener('click', function() {
    isOpen ? closeMenu() : openMenu();
  });

  // Close on Esc
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && isOpen) closeMenu();
  });

  // Close when a menu link is clicked (nav links with href="#...")
  menu.querySelectorAll('a').forEach(function(a) {
    a.addEventListener('click', function() {
      if (isOpen) closeMenu();
    });
  });

  // Focus trapping inside open menu
  document.addEventListener('keydown', function(e) {
    if (!isOpen || e.key !== 'Tab') return;
    var focusable = menu.querySelectorAll('a, button');
    var first = focusable[0];
    var last  = focusable[focusable.length - 1];
    if (e.shiftKey) {
      if (document.activeElement === first) { e.preventDefault(); last.focus(); }
    } else {
      if (document.activeElement === last)  { e.preventDefault(); first.focus(); }
    }
  });
})();
</script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat: mobile menu with focus trap + Esc close + smooth scroll offset"
```

---

### Task 10: Wrap content sections in `<main>` and audit accessibility

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Verify `<main>` landmark is correct**

Search `index.html` for the `<main>` open and close tags. The `<main>` should open just before the features section (`<section class="block" id="features">`) and close before the final CTA (`<section class="final"`).

Run:
```bash
grep -n "<main\|</main\|<header\|</header\|<footer\|<nav\|</nav" index.html
```

Expected: `<header class="hero">` for the hero (correct HTML5 landmark), `<main>` before features, `</main>` after FAQ, `<footer class="site">` for footer.

- [ ] **Step 2: Audit alt text on all images**

```bash
grep -n "<img" index.html
```

Verify every `<img>` has a non-empty `alt` attribute. Decorative images inside `aria-hidden="true"` containers can have `alt=""`.

- [ ] **Step 3: Add `aria-labelledby` to key sections**

The FAQ and Features sections should reference their headings:

```bash
grep -n 'id="features"\|id="faq"\|id="day"\|id="screens"\|id="library"' index.html
```

Each `<section class="block" id="X">` should also have `aria-labelledby="X-heading"`. Add `id="features-heading"` to the Features `<h2>`, `id="day-heading"` to the Day Flow `<h2>`, etc. If this step would create many edits, prioritize features and FAQ.

- [ ] **Step 4: Verify UTM params on all App Store CTAs**

```bash
grep -o 'utm_campaign=[^"&]*' index.html
```

Expected output should include: `home-hero`, `nav`, `mobile-menu`, `final`, `footer`. If any CTA is missing a UTM campaign, add it.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "chore: accessibility audit — landmarks, aria-labelledby, UTM params"
```

---

### Task 11: SEO continuity check + final verification

**Files:**
- Read: `index.html`, `content/*.html`

- [ ] **Step 1: Verify existing content URLs still work**

The existing `content/*.html` files should be unmodified. Confirm:
```bash
ls content/*.html | wc -l
# Should be 26 (the pre-existing articles)
```

- [ ] **Step 2: Verify canonical URL in index.html**

```bash
grep "canonical" index.html
```

Expected: `<link rel="canonical" href="https://jesussays.app/" />`

- [ ] **Step 3: Verify sitemap still covers content pages**

```bash
head -30 sitemap.xml
```

The sitemap should still reference all `/content/*.html` pages. If `index.html` is listed, update its `<loc>` to `https://jesussays.app/` and `<lastmod>` to today's date (2026-05-08).

- [ ] **Step 4: Check llms.txt is still intact**

```bash
head -10 llms.txt
```

This file supports AEO (AI Engine Optimization). Confirm it still references the content pages and add a pointer to the new landing page:

```bash
# Check current content
cat llms.txt
```

If the file references `victorlin-houzz.github.io`, update all occurrences to `jesussays.app`:
```bash
sed -i '' 's/victorlin-houzz\.github\.io/jesussays.app/g' llms.txt
```

- [ ] **Step 5: Update old domain references in index.html (if any remain)**

```bash
grep "victorlin-houzz" index.html
```

If any match: replace with `jesussays.app`.

- [ ] **Step 6: Final commit**

```bash
git add index.html sitemap.xml llms.txt
git commit -m "chore: finalize SEO — canonical URLs, sitemap dates, llms.txt domain"
```

---

### Task 12: Browser smoke test with `/browse` skill

- [ ] **Step 1: Start a local server**

```bash
cd /Users/victor/github/jesussays-website
python3 -m http.server 8080 &
```

- [ ] **Step 2: Run `/browse` skill to open and test the landing page**

Invoke the `browse` skill to navigate to `http://localhost:8080/` and verify:
1. Hero section renders with phone mockup and floating cards
2. Nav is sticky and pill-shaped
3. Features bento grid appears (6-column layout)
4. Gallery horizontal scroll exists
5. Faith Library shows 4 columns with working links
6. FAQ accordion opens/closes
7. At mobile width (≤980px): hamburger visible, nav links hidden
8. Mobile menu opens and closes correctly
9. Final CTA section renders with gold Apple button

- [ ] **Step 3: Stop local server**

```bash
kill %1
```

- [ ] **Step 4: Commit any fixes found during smoke test**

---

## Self-Review Against Spec

### Spec Coverage Check

| Requirement | Task |
|-------------|------|
| Sticky pill nav with frosted backdrop | Task 3 (CSS) + Task 4 (HTML) |
| Brand mark SVG (Y-stem + gold dot) | Task 4 Step 3 |
| Nav CTA with UTM param | Task 4 Step 3 |
| Mobile hamburger → slide-down sheet | Task 3 (CSS) + Task 9 (JS) |
| Focus trapping + Esc in mobile menu | Task 9 |
| Hero 2-col grid, eyebrow chip, H1 with glow span | Task 4 Step 4 |
| Phone mockup with notch + floating cards | Task 4 Step 4 |
| Phone mockup hidden float cards on ≤560px | Task 3 (CSS from reference) |
| Quiet band — Matthew 11:28, gold quotes | Task 5 Step 1 |
| Features bento grid — 7 cards, f1 dark with mic disc | Task 5 Step 2 |
| Day flow — 3 cards with mini phone bezels | Task 6 Step 1 |
| Evening card dark variant | Task 6 Step 1 |
| Gallery — 8 phones, scroll-snap, no scrollbar | Task 6 Step 2 |
| Faith Library — 4 cols, all 18 article links, `/content/` prefix | Task 7 Step 1 |
| FAQ accordion — 6 questions, first open, chevron rotates | Task 7 Step 2 |
| Final CTA — dark bg, gold button, `utm_campaign=final` | Task 8 Step 1 |
| Footer — 4-col, legal row | Task 8 Step 2 |
| `<picture>` + WebP for all 8 screenshots | Tasks 4, 6 |
| Self-hosted fonts, font-display: swap | Tasks 2, 3 |
| Canonical `https://jesussays.app/` | Task 4 Step 1 |
| JSON-LD MobileApplication schema | Task 4 Step 1 |
| Smooth scroll with 90px nav offset | Task 9 |
| Responsive: ≤980px 2-col features, 1-col day grid | Task 3 (CSS from reference) |
| SEO: existing /content/*.html URLs unchanged | Task 11 |
| UTM params: home-hero, nav, mobile-menu, final, footer | Tasks 4–8, 11 |
| `aria-expanded` on hamburger + FAQ | Tasks 4, 7 |
| Alt text on all screenshots | Task 10 |

### Known Open Items (flag before shipping)

- `assets/og-image.png` (1200×630 hero export) — placeholder referenced in `<meta property="og:image">`. Generate or replace before launch.
- Footer Privacy + Terms links point to `#` — fill in when pages exist.
- FAQ Android answer says "drop your email below" — there is no email capture form. Either add one or update the copy.
- Brand mark SVG is a hand-recreation of the app icon. Replace with official brand SVG when available.
