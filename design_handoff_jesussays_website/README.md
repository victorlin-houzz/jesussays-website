# Handoff: Jesus Says — Marketing Website

## Overview

A single-page marketing website for the Jesus Says iOS app. Goal: drive organic web traffic from `www.jesussays.app` (or equivalent) to the App Store listing for downloads, while preserving SEO surface area for prayer/devotional/Bible-verse search queries.

The site mirrors the **visual DNA of the iOS app** — cream paper background, deep ink-blue type, a single warm gold accent dot, Merriweather serif headings + Lato body — so the web → install transition feels continuous.

## About the Design Files

The HTML file in this bundle (`Jesus Says — Website.html`) is a **design reference**, not production code to ship as-is. It is a fully styled, single-file prototype demonstrating intended layout, typography, color, interaction, and responsive behavior.

The implementation task is to **recreate this design in the target codebase's environment** — most likely a static-site or lightweight React/Astro/Next.js setup, since the existing repo (`jesussays-website/`) is a plain HTML site served from GitHub Pages with `/content/*.html` SEO articles. The simplest path: port the design directly into vanilla HTML/CSS that fits alongside the existing `assets/site.css` system. If a richer framework is preferred (Astro recommended for SEO + DX), choose that — but keep the static output and existing `/content/` URL structure intact for SEO continuity.

## Fidelity

**High-fidelity.** The mock specifies final colors, typography, spacing, and interaction states. The developer should recreate it pixel-close. The only invented copy is FAQ answers and benefit phrasing — confirm with marketing before shipping.

## Screens / Views

The site is a single long page with anchor-scroll navigation. Sections, in order:

### 1. Sticky Pill Nav
- **Position**: `position: sticky; top: 14px; z-index: 50;` — floats over content with frosted backdrop
- **Layout**: max-width 1240px, flex row, pill shape (`border-radius: 999px`)
- **Background**: `rgba(251, 247, 236, 0.78)` with `backdrop-filter: saturate(140%) blur(18px)`
- **Border**: `1px solid rgba(26,31,74,0.08)`
- **Shadow**: `0 14px 40px -22px rgba(26,31,74,0.30)`
- **Brand mark**: 32px circle, 1.6px ink-blue stroke, with a 5px gold dot at top inside, and a Y-stem SVG glyph in the center (matches app icon)
- **Brand wordmark**: Merriweather 700, 19px, color `#1A1F4A`
- **Nav links**: Lato 500, 14px, color `#394074`, padding `8px 14px`, hover background `rgba(26,31,74,0.06)` and color `#1A1F4A`. Items: Features · A Daily Practice · App Tour · Faith Library · FAQ
- **CTA button**: ink-blue pill, white text Lato 600 14px, Apple glyph 14px, `padding: 10px 18px`, shadow `0 8px 24px -10px rgba(26,31,74,0.6)`. Hover: lift `translateY(-1px)`, bg `#2A2F5A`
- **Mobile (≤980px)**: hide nav links, show 38px circular hamburger button. Build a slide-down sheet for mobile menu (not in mock — implement using existing patterns)

### 2. Hero
- **Layout**: 2-col grid `1.05fr 1fr`, gap 60px, `padding: 70px 28px 40px`. On ≤980px → 1 col, phone moves to top via `order: -1`
- **Eyebrow chip**: cream paper bg, 1px line border, pill, "Now on iPhone · Free" with a 6px gold dot (`#E89B2C`) glowing via `box-shadow: 0 0 10px rgba(232,155,44,.55)`
- **H1**: Merriweather 700, `clamp(44px, 5.4vw, 76px)`, line-height 1.02, letter-spacing -1.4px, ink. Copy: `Faith answers, <em>for</em> <span class="glow">real life.</span>`. The `em` is italic 400 in `#394074`. The `.glow` span has a horizontal gold gradient bar pseudo-underline.
- **Lede**: 19px Lato 400, color `#394074`, max-width 540px
- **Primary CTA**: ink-blue Apple Store button (16px outer, 14px inner), padding `14px 22px 14px 18px`, radius 14px, two-line stack ("Download on the / **App Store**"), shadow `0 18px 40px -16px rgba(26,31,74,0.55)`. Apple SVG glyph 22px white.
- **Secondary CTA**: ghost link "See a 30-second tour" with a 26px ink-filled circular play badge
- **Trust strip**: 13px warm-grey row of 3 — "Private by default" (shield icon), "Free to download" (check), "iPhone · iOS 16+" (phone icon)
- **Phone mockup** (right):
  - 320px wide, aspect-ratio 320/658, padding 8px, radius 48px
  - Bezel gradient: `linear-gradient(160deg, #2c2f4a, #14172e)`
  - Inner screen: radius 40px, contains `site-assets/home.png`
  - Notch: 96×26px, `#0a0c1d`, radius 14px, top 14px center
  - Stage transform: `rotate(-2deg)` for natural lean
  - Behind phone: gold radial glow `radial-gradient(closest-side, rgba(232,155,44,0.20), transparent 70%)` blurred 40px
  - **Three floating glass cards** (`.fc-1`, `.fc-2`, `.fc-3`) — paper bg, 1px line, radius 18px, 36px icon tile + 14px serif title + 12px subtitle. Captions: "Talk to Jesus / 90-second voice prayer" (gold icon), "Verse for this moment / — Matthew 11:28", "3-minute reflection / Begin your morning rhythm". Slight tilts (-3°, +2°, -1.5°). Hidden on ≤560px.

### 3. Quiet Band (Scripture)
- Full-bleed, 90px vertical padding
- Background: `radial-gradient(ellipse at top, rgba(232,155,44,0.10), transparent 60%)` over paper `#FBF7EC`
- Top + bottom 1px hairline borders
- Verse: Merriweather 400 italic, `clamp(26px, 3.4vw, 42px)`, line-height 1.35, ink, max-width 880px, balanced wrap. Copy: "Come unto me, all ye that labour and are heavy laden, and I will give you rest." Quote marks colored gold, non-italic.
- Attribution: 13px Lato 700, uppercase, letter-spacing 1.6px, warm-grey, with a 28×1px rule before the text. Reads `MATTHEW 11:28`.

### 4. Features (Bento Grid)
- **Section header pattern** (reused throughout):
  - Tag: `text-transform: uppercase; letter-spacing: 1.8px; color: #E89B2C` with a 6px gold dot prefix
  - H2: Merriweather 700, `clamp(32px, 3.8vw, 52px)`, line-height 1.05, letter-spacing -0.8px
  - Right-side support copy: 16px Lato 400, color `#394074`, max-width 380px
  - Hairline border underneath, padding-bottom 22px, margin-bottom 56px
- **Grid**: 6-column, `grid-auto-rows: 280px`, gap 18px
- **Card classes** (CSS grid spans):
  - `.f1` — 3 cols × 2 rows · **dark `#0F1437` "Talk to Jesus" signature card.** White text. Title 36px. Bottom-right: 110px gold disc with 48px mic SVG, 12px gold halo, plus two outer thin gold rings. Background gold radial. Italic "— 01" label top.
  - `.f2` — 3 cols × 1 row · "Receive Scripture for your exact moment." Includes a `verse-mini` card preview (white bg, 6px gold dot, italic Merriweather quote with uppercase eyebrow "FOR WHEN YOU'RE WEARY")
  - `.f3` — 2 cols · "A sacred space for personal reflection."
  - `.f4` — 2 cols · "Choose your devotion journey." (Foundations · Daily Strength · Deep Study)
  - `.f5` — 2 cols · "The whole Bible — verse by verse." (KJV)
  - `.f6` — 3 cols · "Build a daily faith rhythm — sustainable." Cream-2 bg `#F6F1E4`. Includes 3 chips: "Streaks (no shame)", "Smart reminders", "Offline-friendly"
  - `.f7` — 3 cols · "Private by default. No ads. No tracking." Chips: "On-device journal", "No data sold", "Delete anytime"
- **Card chrome**: paper bg `#FBF7EC`, 1px line, radius 24px, padding 26px. Top-right: 44px square `rgba(26,31,74,0.06)` icon tile with 22px stroke icon. Italic Merriweather "— 0N" item number above title.
- **Hover**: `translateY(-3px)` + shadow
- **Mobile ≤980px**: 2-col grid, all cards span 1 except `.f1`, `.f2`, `.f6`, `.f7` which span 2. Min-height 220px (380px for `.f1`).
- **≤560px**: 1-column

### 5. A Day with Jesus Says
- 3-col grid, gap 24px
- Each card: paper bg, 1px line, radius 24px, padding `28px 26px 0`
- **Step header**: 22px ink circle with white digit (`#1A1F4A` bg, gold for evening card) + uppercase warm-grey "MORNING · 3 MIN"
- **Title**: Merriweather 700, 26px
- **Body copy**: 14.5px ink-soft
- **Mini phone**: 220px wide, aspect 220/460, radius 36px, dark bezel gradient, inside a 360px-tall masked window (`object-position: top` on the screen image)
- **Card 3 ("Evening · 5 min")** uses dark variant: `#0F1437` bg, white title, gold step dot, gold-soft step label
- Screens used (in order): `devotion-paths.png`, `reflection.png`, `result.png`

### 6. App Tour Gallery
- Section header inside `.block`, but the gallery itself is full-bleed `.gallery-wrap`
- Horizontal scroll-snap row of 8 phone bezels, gap 28px, `padding: 16px 28px 60px`
- Each bezel: 280px wide, aspect 280/580, radius 42px, dark gradient bezel, inner screen radius 36px (object-position top)
- Below each: italic Merriweather 14px caption in warm-grey, absolutely positioned `bottom: -36px`
- Hide scrollbar (`scrollbar-width: none`), enable `scroll-snap-type: x mandatory`
- Order: Welcome · Home · Devotion Journey · Personal Reflection · Your Reflection · Holy Bible · Journal · Talk to Jesus

### 7. Faith Library (SEO Hub)
- Full-bleed band: paper bg, top + bottom 1px borders, 90px vertical padding
- 4-col grid, gap 28px
- Each col header: Merriweather 700 18px, with leading 6px gold dot, 12px bottom padding + 1px line separator
- Items: 14.5px ink-soft, 7px vertical spacing, hover → ink color + arrow appears (gap animates)
- Foot CTA: pill button "Browse the full library →" linking to `content/index.html`
- **Links wired** (all relative, matching existing repo structure):
  - Bible verses: `bible-verses-anxiety.html`, `bible-verses-for-strength-hard-times.html`, `bible-verses-about-faith-and-trust.html`, `bible-verses-about-peace-and-fear.html`
  - Prayer: `prayer-for-healing.html`, `morning-prayer-for-protection.html`, `night-prayer-for-sleep-and-anxiety.html`, `prayer-for-depression-and-hopelessness.html`, `prayer-for-family-and-marriage.html`
  - Confession: `confession-prayer-guide.html`, `confession-prayer-after-failure.html`, `confession-prayer-for-addiction-recovery.html`, `love-and-forgiveness.html`
  - Devotionals: `daily-devotional-today.html`, `daily-devotional-on-financial-stress.html`, `daily-devotional-on-forgiveness.html`, `daily-devotional-on-purpose.html`, `christian-advice-for-relationships.html`

### 8. FAQ
- Native `<details>` accordion, max-width 880px centered
- Each item: top + bottom 1px hairline, 22px vertical padding
- Summary: Merriweather 700 19px, ink, 18px gap, hides default marker
- Trailing chevron: 14px SVG, rotates 180° when `[open]`
- Body: 16px ink-soft, line-height 1.6, max-width 720px
- Default open: question 1 ("Is Jesus Says free?")
- Questions: free?, privacy?, replacement-for-church?, translation?, Android?, cancel?

### 9. Final CTA
- Margin: `110px 28px 28px`, radius 32px
- Background: `#0F1437` with two radial gold glows at 20%/30% and 80%/80%
- Center stack: 56px circle "star" with gold dot inside + circle SVG behind, H2 (`clamp(36px, 4.6vw, 60px)` Merriweather, with italic gold-soft em "A quieter year ahead."), 17px lede, gold Apple Store button (`#E89B2C` bg, ink text), small print legal note

### 10. Footer
- Max-width 1240px, 4-col grid `1.4fr 1fr 1fr 1fr`, gap 48px, 60px padding, top 1px line
- Col 1: brand block + meta paragraph
- Cols 2-4: App / Library / Company link lists, Merriweather 14px headers
- Legal row: full-width, 1px top line, 28px padding-top, justified between copyright and link cluster
- Mobile: 2-col → 1-col

## Interactions & Behavior

- **Smooth scroll** on hash links with 90px sticky-nav offset (small inline JS at end of file)
- **Card hovers**: `translateY(-3px)` + softer-to-stronger shadow ramp, 250ms transition
- **Library link hover**: color brightens, gap widens from 8px → 12px, arrow `→` fades in
- **Apple CTA hover**: `translateY(-2px)` + amplified shadow
- **FAQ chevron**: 200ms rotation
- **Gallery**: native scroll-snap (no JS); each phone tile has `transform: translateY(-6px)` on hover
- **Nav burger** on mobile: tool-time stub — implement a slide-down sheet using existing component patterns

## State Management

Static site, no client state. Single inline JS handler hijacks anchor clicks for offset smooth-scroll. Everything else is CSS.

If migrating to a framework, the only stateful piece is the FAQ accordion (already covered by `<details>`) and the mobile nav menu (open/closed boolean).

## Design Tokens

```css
/* Color */
--cream:        #EFE9DC;   /* page bg */
--cream-2:      #F6F1E4;   /* slightly warmer card bg */
--paper:        #FBF7EC;   /* lightest paper, used for nav + cards */
--ink:          #1A1F4A;   /* primary text + buttons */
--ink-2:        #2A2F5A;   /* button hover */
--ink-soft:     #394074;   /* secondary text */
--gold:         #E89B2C;   /* signature accent dot + halos */
--gold-soft:    #F4C875;   /* soft gold (italic em on dark bg) */
--warm-grey:    #6B6658;   /* tertiary / metadata */
--warm-grey-2:  #8B8676;   /* even softer */
--line:         rgba(26,31,74,0.10);
--night:        #0F1437;   /* dark "signature" card + final CTA */
--night-2:      #161B45;

/* Type */
--serif:  'Merriweather', 'Iowan Old Style', Georgia, serif;
--sans:   'Lato', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;

/* Radii */
--r-sm: 10px;  --r: 16px;  --r-lg: 24px;  --r-xl: 32px;

/* Layout */
--maxw: 1240px;
```

**Typography scale**:
- Hero H1: `clamp(44px, 5.4vw, 76px)` Merriweather 700, ls -1.4px, lh 1.02
- Section H2: `clamp(32px, 3.8vw, 52px)` Merriweather 700, ls -0.8px, lh 1.05
- Card H3: 22-26px Merriweather 700, ls -0.3px to -0.4px, lh 1.18
- Big quote: `clamp(26px, 3.4vw, 42px)` Merriweather 400 italic
- Body: 16-19px Lato 400, lh 1.55
- Eyebrow / tag: 12-13px Lato 700, uppercase, ls 1.6-1.8px
- Footer / meta: 13-14px Lato

**Shadows**:
- Phone: `0 60px 120px -30px rgba(26,31,74,0.45)` + `0 30px 60px -20px rgba(26,31,74,0.25)`
- Float card: `0 22px 50px -18px rgba(26,31,74,0.30)`
- Apple CTA: `0 18px 40px -16px rgba(26,31,74,0.55)` (lifts to `0 24px 48px -16px ...` on hover)
- Card hover: `0 24px 50px -28px rgba(26,31,74,0.30)`
- Gold mic glow: `0 0 0 12px rgba(232,155,44,0.18), 0 30px 60px -10px rgba(232,155,44,0.45)`

**Spacing**: section vertical rhythm is 90-110px; card padding 26-36px; nav padding 10-22px.

## Assets

All app screenshots in `site-assets/` were exported from the iOS app design at native resolution (1320×2868):

| File | Used in |
|---|---|
| `welcome.png` | Gallery |
| `home.png` | Hero phone, Gallery |
| `devotion-paths.png` | Day flow card 1, Gallery |
| `reflection.png` | Day flow card 2, Gallery |
| `result.png` | Day flow card 3, Gallery |
| `bible.png` | Gallery |
| `journal.png` | Gallery |
| `chat.png` | Gallery |

**Logo glyph**: vector recreation of the app icon (circle with Y-stem and orange dot) in inline SVG. Replace with the official brand SVG when available — the path is hand-recreated.

**Apple SVG glyph**: standard SF-style apple, embedded inline.

All other iconography is **inline 24px stroke SVG** (`stroke-width: 2`, `linecap: round`, `linejoin: round`) — replace with Lucide or whatever icon set the codebase already uses.

**Fonts**: Google Fonts (`Lato`, `Merriweather`). For production, self-host or use `next/font` to avoid CLS.

## Files

- `Jesus Says — Website.html` — single-file design reference (~48KB, no external JS deps beyond Google Fonts)
- `site-assets/` — 8 PNG screenshots from the iOS app

## Recommended Implementation Path

1. **Drop the HTML directly** into the existing `jesussays-website/` repo as `landing.html` or replace `index.html` (keep current `index.html` as `library.html` for SEO continuity, or migrate its links into the Faith Library section as already done).
2. **Inline the CSS into `assets/site.css`** under a namespaced section, or split into `assets/landing.css` to avoid colliding with the article-page styles.
3. **Self-host fonts** — Lato + Merriweather subsets — to remove the Google Fonts request.
4. **Compress screenshots** — current PNGs are ~4.5MB each at 1320×2868. Re-export at 880×1916 and convert to WebP/AVIF; they only render at ~280-320px wide.
5. **Verify SEO**: keep `<title>`, meta description, canonical, and JSON-LD `MobileApplication` schema from the existing `download.html`.
6. **Track conversions**: keep the `?utm_source=website&utm_medium=cta&utm_campaign=...` query params on every App Store link (already wired).

## Open Questions for the Developer / PM

- Is there a real brand SVG for the Jesus Says logo? Inline glyph is a hand recreation.
- App Store rating / install count — worth surfacing in the hero trust strip once available.
- Is there short-form **video** for the "See a 30-second tour" CTA, or should it scroll-anchor to the gallery (current behavior)?
- FAQ answers are best-guess copy — confirm with marketing/legal before shipping.
- Confirm App Store ID `id6756906208` is final.
