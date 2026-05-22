#!/usr/bin/env python3
"""Seed competitor-inspired Jesus Says content opportunities.

The seed data uses competitor crawl findings as demand signals. It does not copy
competitor content. Each row is an original Jesus Says article opportunity.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

OUTPUT = Path("content/opportunities.jsonl")


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


TOPICS = [
    ("anxiety", "emotional care", 98, "https://www.bible.com/reading-plans-collection/812-anxiety", "YouVersion reading plan collection: Anxiety"),
    ("healing", "prayer", 96, "https://www.bible.com/reading-plans-collection/845-healing", "YouVersion reading plan collection: Healing"),
    ("love", "relationships", 94, "https://www.bible.com/reading-plans-collection/782-love", "YouVersion reading plan collection: Love"),
    ("depression", "emotional care", 94, "https://www.bible.com/reading-plans-collection/809-depression", "YouVersion reading plan collection: Depression"),
    ("fear", "emotional care", 92, "https://www.bible.com/reading-plans-collection/849-fear", "YouVersion reading plan collection: Fear"),
    ("peace", "emotional care", 92, "https://www.bible.com/reading-plans-collection/290-peace", "YouVersion reading plan collection: Peace"),
    ("stress", "emotional care", 90, "https://www.bible.com/reading-plans-collection/866-stress", "YouVersion reading plan collection: Stress"),
    ("hope", "emotional care", 90, "https://www.bible.com/reading-plans-collection/906-hope", "YouVersion reading plan collection: Hope"),
    ("anger", "emotional care", 86, "https://www.bible.com/reading-plans-collection/848-anger", "YouVersion reading plan collection: Anger"),
    ("loss", "grief", 86, "https://www.bible.com/reading-plans-collection/905-loss", "YouVersion reading plan collection: Loss"),
    ("patience", "spiritual growth", 82, "https://www.bible.com/reading-plans-collection/899-patience", "YouVersion reading plan collection: Patience"),
    ("temptation", "spiritual growth", 82, "https://www.bible.com/reading-plans-collection/916-temptation", "YouVersion reading plan collection: Temptation"),
    ("doubt", "spiritual growth", 80, "https://www.bible.com/reading-plans-collection/919-doubt", "YouVersion reading plan collection: Doubt"),
    ("relationships", "relationships", 88, "https://www.bible.com/reading-plans-collection/1386", "YouVersion reading plan collection: Relationships"),
    ("new faith", "discipleship", 84, "https://www.bible.com/reading-plans-collection/1676", "YouVersion reading plan collection: New to Faith"),
    ("prayer life", "prayer", 90, "https://hallow.com/blog/?category_name=prayer-life", "Hallow prayer life blog category"),
    ("fasting", "seasonal", 78, "https://hallow.com/blog/prayers-for-fasting/", "Hallow article: Prayers for Fasting"),
    ("lent", "seasonal", 76, "https://hallow.com/lent/", "Hallow Lent guide"),
    ("holy week", "seasonal", 74, "https://hallow.com/blog/holy-week-schedule/", "Hallow Holy Week guide"),
    ("good friday", "seasonal", 72, "https://hallow.com/blog/good-friday-the-passion-of-christ/", "Hallow Good Friday guide"),
    ("holy thursday", "seasonal", 70, "https://hallow.com/blog/holy-thursday/", "Hallow Holy Thursday guide"),
    ("easter vigil", "seasonal", 70, "https://hallow.com/blog/easter-vigil/", "Hallow Easter Vigil guide"),
    ("rosary", "prayer", 68, "https://hallow.com/blog/how-to-pray-the-rosary/", "Hallow Rosary guide"),
    ("sharing faith at work", "work", 78, "https://www.bible.com/reading-plans/71857-a-firm-foundation-for-sharing-jesus-at-work", "YouVersion plan: Sharing Jesus at Work"),
    ("purpose", "calling", 88, "https://www.bible.com/reading-plans/71073-your-talents-have-a-purpose", "YouVersion plan: Your Talents Have a Purpose"),
    ("knowing god", "discipleship", 80, "https://www.bible.com/reading-plans/71668-knowing-god", "YouVersion plan: Knowing God"),
    ("holy spirit", "spiritual growth", 78, "https://www.bible.com/reading-plans/70801-7-things-the-holy-spirit-does-in-you", "YouVersion plan: Holy Spirit"),
    ("baptism", "new faith", 70, "https://www.bible.com/reading-plans/71849-baptism-home-in-him", "YouVersion plan: Baptism"),
    ("acts", "bible study", 76, "https://www.bible.com/reading-plans-collection/729", "YouVersion reading plan collection: Acts"),
    ("rest", "emotional care", 84, "https://blog.youversion.com/category/rest/", "YouVersion blog category: Rest"),
]

FORMATS = [
    ("bible-verses", "Bible Verses for {topic_title}", "bible verses for {topic}", "Bible Verses", "Find Scripture for {topic} and receive a personalized verse in Jesus Says when your situation feels specific."),
    ("prayer", "A Prayer for {topic_title}", "prayer for {topic}", "Prayer", "Use Jesus Says voice prayer and journaling to turn this prayer into a daily rhythm."),
    ("devotional", "Daily Devotional on {topic_title}", "daily devotional on {topic}", "Devotional", "Invite readers to continue with daily devotion paths and personalized reflection in the app."),
    ("what-does-the-bible-say", "What Does the Bible Say About {topic_title}?", "what does the bible say about {topic}", "Christian Advice", "Position Jesus Says as the next step for asking a personal Scripture question."),
    ("how-to-pray", "How to Pray About {topic_title}", "how to pray about {topic}", "Prayer", "Connect practical prayer steps to the app's voice prayer and confession journal."),
    ("jesus-says", "What Would Jesus Say About {topic_title}?", "what would jesus say about {topic}", "AEO Question", "This directly matches Jesus Says app positioning: bring a real moment and receive Scripture-grounded reflection."),
    ("night-prayer", "Night Prayer for {topic_title}", "night prayer for {topic}", "Prayer", "Use sleep/anxiety moments to introduce short evening reflection in the app."),
    ("morning-prayer", "Morning Prayer for {topic_title}", "morning prayer for {topic}", "Prayer", "Use morning intent to introduce reminders and daily Scripture rhythm in the app."),
    ("confession", "Confession Prayer for {topic_title}", "confession prayer for {topic}", "Confession", "Route shame, relapse, anger, and failure topics to private confession journaling."),
    ("christian-advice", "Christian Advice for {topic_title}", "christian advice for {topic}", "Christian Advice", "Offer practical, pastoral steps and invite personalized Scripture reflection in Jesus Says."),
    ("verses-and-prayer", "Bible Verses and Prayer for {topic_title}", "bible verses and prayer for {topic}", "Bible Verses", "Blend high-intent verse search with app CTA for personalized prayer prompts."),
    ("devotional-plan", "7-Day Devotional for {topic_title}", "7 day devotional for {topic}", "Devotional", "Point readers to devotion paths and daily app use without overpromising outcomes."),
    ("questions", "Questions Christians Ask About {topic_title}", "christian questions about {topic}", "FAQ", "Build answer-engine coverage with concise FAQs and app-supported next steps."),
    ("scripture-reflection", "Scripture Reflection for {topic_title}", "scripture reflection for {topic}", "Devotional", "Frame Jesus Says as a reflection companion for the user's exact situation."),
    ("short-prayer", "Short Prayer for {topic_title}", "short prayer for {topic}", "Prayer", "High-conversion short prayer format, ending with app-based voice prayer."),
    ("psalms", "Psalms for {topic_title}", "psalms for {topic}", "Bible Verses", "Use Psalms as an entry point into personalized Scripture discovery."),
    ("when-you-feel", "When You Feel {topic_title}: Bible Help for Today", "when you feel {topic}", "AEO Question", "Meet the reader in an emotional moment and invite a personal verse in the app."),
]

SEASONAL_HINTS = {
    "lent": "lent",
    "holy week": "easter",
    "good friday": "easter",
    "holy thursday": "easter",
    "easter vigil": "easter",
    "fasting": "lent",
    "prayer life": "evergreen",
}

SKIP_COMBOS = {
    ("rosary", "confession"),
    ("rosary", "night-prayer"),
    ("rosary", "morning-prayer"),
    ("acts", "confession"),
    ("baptism", "night-prayer"),
}


def source_site(url: str) -> str:
    if "hallow.com" in url:
        return "Hallow"
    if "bible.com" in url or "youversion" in url:
        return "YouVersion"
    return "Competitor"


def intent_for(fmt_slug: str, topic: str) -> str:
    if fmt_slug in {"bible-verses", "verses-and-prayer", "psalms"}:
        return "Find Scripture passages for a specific real-life situation."
    if "prayer" in fmt_slug:
        return "Find a prayer to say in a specific situation."
    if "devotional" in fmt_slug or fmt_slug == "scripture-reflection":
        return "Find a short devotional reflection and next step."
    if fmt_slug == "jesus-says":
        return "Ask what Jesus or Scripture would say about a real-life concern."
    return "Get Christian guidance for a practical or emotional question."


def build_rows() -> list[dict]:
    rows: list[dict] = []
    seen_slugs: set[str] = set()
    today = date.today().isoformat()
    for topic, category, base_priority, url, source_title in TOPICS:
        topic_title = topic.title()
        for fmt_slug, title_template, keyword_template, content_type, cta in FORMATS:
            if (topic, fmt_slug) in SKIP_COMBOS:
                continue
            title = title_template.format(topic_title=topic_title)
            keyword = keyword_template.format(topic=topic)
            slug = slugify(title)
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            priority = max(35, min(100, base_priority - FORMATS.index((fmt_slug, title_template, keyword_template, content_type, cta)) * 2))
            rows.append({
                "id": f"opp-{len(rows)+1:04d}",
                "status": "discovered",
                "source_site": source_site(url),
                "source_url": url,
                "source_title": source_title,
                "source_category": category,
                "detected_intent": intent_for(fmt_slug, topic),
                "jesus_says_title": title,
                "target_slug": slug,
                "primary_keyword": keyword,
                "secondary_keywords": [
                    f"scripture for {topic}",
                    f"christian help for {topic}",
                    f"jesus says {topic}",
                ],
                "content_type": content_type,
                "user_need": f"The reader wants Bible-grounded help for {topic} without generic religious filler.",
                "jesus_says_angle": f"Create an original Jesus Says article that answers the query quickly, gives Scripture and prayer steps, and speaks to the reader's exact moment around {topic}.",
                "app_cta_angle": cta.format(topic=topic),
                "priority": priority,
                "seasonality": SEASONAL_HINTS.get(topic, "evergreen"),
                "notes": "Competitor URL is a demand signal only. Do not copy wording, structure, or proprietary devotional material.",
                "created_at": today,
                "published_at": "",
            })
            if len(rows) >= 500:
                return rows
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite an existing opportunities tracker")
    args = parser.parse_args()
    if OUTPUT.exists() and not args.force:
        raise SystemExit(f"{OUTPUT} already exists. Use --force only when intentionally reseeding.")
    rows = build_rows()
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(f"Wrote {len(rows)} opportunities to {OUTPUT}")


if __name__ == "__main__":
    main()
