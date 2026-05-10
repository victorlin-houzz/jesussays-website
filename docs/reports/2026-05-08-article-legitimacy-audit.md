# Jesus Says Article Legitimacy Audit — 2026-05-08

## Scope

Reviewed all 24 existing article pages under `content/*.html`, excluding `content/index.html` and `content/keyword-clusters.html`.

## Result

All 24 articles are coherent and usable after cleanup. The site had no wholesale nonsense pages, fake-looking generated gibberish, or broken article structure. The fixes were mostly quality/safety tightening:

- softened overpromising language around anxiety, peace, healing, and strength
- removed mechanistic phrases like “activates” and “converts anxiety”
- added crisis/professional-care boundaries to depression, anxiety, addiction, burnout, loneliness, healing, money, and marriage/family pages
- corrected proof-text/context issues around Jeremiah 29:11, Revelation 3:8, James 2:13, Psalm 139, Elijah, and healing language
- removed JSON-LD `&quot;` artifacts
- softened unsupported clinical/research-style claims
- added abuse/coercive-control boundaries where reconciliation language appears

## Files Updated

- `content/bible-verses-about-faith-and-trust.html`
- `content/bible-verses-about-peace-and-fear.html`
- `content/bible-verses-anxiety.html`
- `content/bible-verses-for-anxiety-about-money.html`
- `content/bible-verses-for-job-loss-and-unemployment.html`
- `content/bible-verses-for-loneliness-and-isolation.html`
- `content/bible-verses-for-strength-hard-times.html`
- `content/christian-advice-for-anxiety-at-work.html`
- `content/confession-prayer-for-addiction-recovery.html`
- `content/confession-prayer-guide.html`
- `content/daily-devotional-on-forgiveness.html`
- `content/daily-devotional-on-purpose.html`
- `content/daily-devotional-today.html`
- `content/how-to-pray-according-to-the-bible.html`
- `content/jesus-quotes-on-love-mercy-and-truth.html`
- `content/love-and-forgiveness.html`
- `content/prayer-for-depression-and-hopelessness.html`
- `content/prayer-for-family-and-marriage.html`
- `content/prayer-for-healing.html`

## Pages Audited With No Material Changes Required

- `content/christian-advice-for-relationships.html`
- `content/confession-prayer-after-failure.html`
- `content/daily-devotional-on-financial-stress.html`
- `content/morning-prayer-for-protection.html`
- `content/night-prayer-for-sleep-and-anxiety.html`

## Verification

```bash
python3 scripts/check_aeo.py
# 24/24 pages pass AEO checks.
```

Risk scan after patch found no remaining hits for the targeted unsafe/low-quality phrases:

```bash
rg -n "activates|converts anxiety|nervous system God|physically reduces|asked to die from loneliness|Vague prayers reflect|Psalm 139 describe|strongest predictors|Refusing rest is often|within any workload|Peace is possible right now|Anxiety finds a direct answer|lasting freedom|speaks for Jesus|replaces church|replaces pastoral care|cures|most accurate|better than" content/*.html
# no matches
```

## Recommendation

Safe to keep these articles indexed. Before publishing more AI-generated faith content, add a required post-generation quality pass for:

1. Scripture reference/context fit
2. no medical, financial, or legal overclaims
3. crisis/abuse/professional-care boundaries where needed
4. no “Jesus speaks through the app” implication
5. no unsupported research/clinical claims
6. no encoded artifacts in JSON-LD
