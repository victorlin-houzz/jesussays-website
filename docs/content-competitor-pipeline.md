# Competitor-Informed Content Pipeline

Goal: grow Jesus Says organic traffic and app downloads by using competitor pages as demand signals, then publishing original Jesus Says articles optimized for Google Search and answer engines.

## Workflow

1. Crawl competitor hubs with the project-approved `/browse` workflow.
2. Extract URL, title, category, and inferred intent.
3. Convert each source into an original Jesus Says opportunity in `content/opportunities.jsonl`.
4. Score opportunities by search intent, app fit, seasonality, and conversion value.
5. Generate 10-20 opportunities at a time with `scripts/generate_opportunity_articles.py`.
6. Audit every draft with `scripts/audit_generated_articles.py` and `scripts/check_aeo.py`.
7. Mark opportunities as `drafted`, `published`, `refreshed`, or `skipped` only after checks pass.

## Originality Rules

Competitor pages are never templates to copy. They are evidence that people search for a topic. Jesus Says articles must use original structure, wording, Scripture selection, FAQs, pastoral care notes, and app calls to action.

## Files

- `content/opportunities.jsonl`: long-lived metadata tracker.
- `scripts/seed_opportunities.py`: deterministic seed generator for the first 500 opportunities.
- `scripts/manage_opportunities.py`: validate, inspect, promote, and mark opportunity progress.
- `scripts/generate_opportunity_articles.py`: batch generator that writes articles, sitemap entries, `llms.txt`, and Faith Library links.
- `scripts/audit_generated_articles.py`: SEO/AEO, CTA, JSON-LD, duplicate-source, and sensitive-topic audit gate.
- `content/queue.json`: legacy publishing queue consumed by the older article generator.

## Commands

Validate the tracker:

```bash
python3 scripts/manage_opportunities.py validate
```

Show status/source/type counts:

```bash
python3 scripts/manage_opportunities.py stats
```

See the next 20 highest-priority discovered opportunities:

```bash
python3 scripts/manage_opportunities.py next --limit 20
```

Generate the next 10 opportunities:

```bash
python3 scripts/generate_opportunity_articles.py --limit 10
```

Use deterministic local rendering when the content model returns malformed output or is unavailable:

```bash
python3 scripts/generate_opportunity_articles.py --limit 10 --local-only
```

Audit drafts before publishing:

```bash
python3 scripts/audit_generated_articles.py --status drafted
python3 scripts/check_aeo.py
python3 scripts/audit_generated_articles.py --status drafted --mark-published
```

## Initial Competitor Signals

The first seed list uses live crawl samples from:

- Hallow blog: prayer life, Lent, fasting, Holy Week, Good Friday, Holy Thursday, Easter Vigil, Rosary.
- YouVersion blog and Bible.com reading-plan collections: anxiety, healing, love, depression, fear, peace, stress, hope, anger, loss, patience, temptation, doubt, relationships, new faith, Acts, work, purpose, Holy Spirit, baptism.
- Glorify public blog/app positioning: devotional habit and app-comparison angles.

## Batch Publishing Guidance

For each batch, prefer 10-20 articles. Start with high-conversion emotional and prayer topics before broad Bible-study topics:

1. Anxiety, depression, fear, peace, stress, healing.
2. Prayer formats: short prayer, night prayer, morning prayer, how to pray.
3. Relationship and work topics.
4. Seasonal guides when the calendar is near Lent, Holy Week, Easter, Advent, Christmas, or New Year.
5. Comparison/app intent pages when they can honestly explain where Jesus Says is different.

## Duplicate And Progress Rules

Do not rerun `scripts/seed_opportunities.py --force` after work has begun unless intentionally rebuilding the tracker from scratch. The generator and manager skip existing, drafted, published, queued, and near-duplicate slugs using normalized topic slugs. Before every new crawl import, run:

```bash
python3 scripts/manage_opportunities.py dedupe
python3 scripts/manage_opportunities.py validate
```

The first audited batch published 10 of 500 opportunities on 2026-05-22. Future batches should continue from `discovered` rows and never overwrite `published_at` progress without an explicit refresh plan.
