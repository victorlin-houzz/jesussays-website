#!/usr/bin/env python3
"""Manage Jesus Says competitor-inspired content opportunities.

The tracker is metadata-only. Competitor URLs identify demand and intent; generated
Jesus Says articles must be original and tailored to the app's Scripture/prayer use case.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

OPPORTUNITIES_PATH = Path("content/opportunities.jsonl")
QUEUE_PATH = Path("content/queue.json")
VALID_STATUSES = {
    "discovered",
    "briefed",
    "queued",
    "drafted",
    "published",
    "refreshed",
    "skipped",
}
REQUIRED_FIELDS = [
    "id",
    "status",
    "source_site",
    "source_url",
    "source_title",
    "source_category",
    "detected_intent",
    "jesus_says_title",
    "target_slug",
    "primary_keyword",
    "secondary_keywords",
    "content_type",
    "user_need",
    "jesus_says_angle",
    "app_cta_angle",
    "priority",
    "seasonality",
    "notes",
    "created_at",
    "published_at",
]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def load_opportunities(path: Path = OPPORTUNITIES_PATH) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        rows.append(row)
    return rows


def write_opportunities(rows: list[dict[str, Any]], path: Path = OPPORTUNITIES_PATH) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def load_queue(path: Path = QUEUE_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def write_queue(rows: list[dict[str, Any]], path: Path = QUEUE_PATH) -> None:
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(rows: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    ids: Counter[str] = Counter()
    slugs: Counter[str] = Counter()
    for index, row in enumerate(rows, 1):
        for field in REQUIRED_FIELDS:
            if field not in row:
                issues.append(f"row {index}: missing {field}")
        row_id = str(row.get("id", ""))
        slug = str(row.get("target_slug", ""))
        ids[row_id] += 1
        slugs[slug] += 1
        if row.get("status") not in VALID_STATUSES:
            issues.append(f"{row_id}: invalid status {row.get('status')!r}")
        if slug and slug != slugify(slug):
            issues.append(f"{row_id}: target_slug is not slugified: {slug}")
        if not isinstance(row.get("secondary_keywords"), list):
            issues.append(f"{row_id}: secondary_keywords must be a list")
        priority = row.get("priority")
        if not isinstance(priority, int) or priority < 1 or priority > 100:
            issues.append(f"{row_id}: priority must be an integer from 1 to 100")
        if row.get("published_at") not in (None, "") and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(row.get("published_at"))):
            issues.append(f"{row_id}: published_at must be blank/null or YYYY-MM-DD")
    for row_id, count in ids.items():
        if row_id and count > 1:
            issues.append(f"duplicate id: {row_id}")
    for slug, count in slugs.items():
        if slug and count > 1:
            issues.append(f"duplicate target_slug: {slug}")
    return issues


def cmd_validate(_: argparse.Namespace) -> int:
    rows = load_opportunities()
    issues = validate(rows)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print(f"OK: {len(rows)} opportunities")
    return 0


def cmd_stats(_: argparse.Namespace) -> int:
    rows = load_opportunities()
    print(f"total: {len(rows)}")
    for label, counter in [
        ("status", Counter(row["status"] for row in rows)),
        ("source_site", Counter(row["source_site"] for row in rows)),
        ("content_type", Counter(row["content_type"] for row in rows)),
        ("seasonality", Counter(row["seasonality"] for row in rows)),
    ]:
        print(f"\n{label}:")
        for key, count in counter.most_common():
            print(f"  {key}: {count}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    rows = [row for row in load_opportunities() if row["status"] == args.status]
    rows.sort(key=lambda row: (-row["priority"], row["id"]))
    for row in rows[: args.limit]:
        print(f"{row['id']} | P{row['priority']} | {row['primary_keyword']} | {row['target_slug']}")
    return 0


STOP_SLUG_WORDS = {"a", "an", "the", "for", "about", "on", "and", "to", "of", "in"}


def normalized_topic_slug(slug: str) -> str:
    return "-".join(part for part in slugify(slug).split("-") if part not in STOP_SLUG_WORDS)


def existing_content_slugs() -> set[str]:
    skip = {"index", "keyword-clusters"}
    return {path.stem for path in Path("content").glob("*.html") if path.stem not in skip}


def cmd_dedupe(_: argparse.Namespace) -> int:
    rows = load_opportunities()
    existing = existing_content_slugs()
    queued = {item["slug"] for item in load_queue()}
    existing_normalized = {normalized_topic_slug(slug) for slug in existing | queued}
    changed = 0
    for row in rows:
        reason = ""
        if row["target_slug"] in existing:
            reason = "an article with this slug already exists"
        elif row["target_slug"] in queued:
            reason = "this slug is already in content/queue.json"
        elif normalized_topic_slug(row["target_slug"]) in existing_normalized:
            reason = "a near-duplicate article/topic already exists or is queued"
        if row["status"] == "discovered" and reason:
            row["status"] = "skipped"
            row["notes"] = (row.get("notes") or "") + f" Skipped because {reason}."
            changed += 1
    write_opportunities(rows)
    print(f"Marked {changed} duplicate opportunities as skipped")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    rows = load_opportunities()
    issues = validate(rows)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    queue = load_queue()
    existing_slugs = existing_content_slugs()
    queued_slugs = {item["slug"] for item in queue}
    blocked_slugs = existing_slugs | queued_slugs
    blocked_normalized = {normalized_topic_slug(slug) for slug in blocked_slugs}
    candidates = [row for row in rows if row["status"] == "discovered" and row["target_slug"] not in blocked_slugs and normalized_topic_slug(row["target_slug"]) not in blocked_normalized]
    if args.min_priority is not None:
        candidates = [row for row in candidates if row["priority"] >= args.min_priority]
    candidates.sort(key=lambda row: (-row["priority"], row["id"]))
    chosen = candidates[: args.limit]

    for row in chosen:
        queue.append({
            "keyword": row["primary_keyword"],
            "slug": row["target_slug"],
            "status": "pending",
            "volume_est": row["priority"] * 100,
            "opportunity_id": row["id"],
        })
        row["status"] = "queued"
        row["notes"] = (row.get("notes") or "") + f" Promoted to content/queue.json on {date.today().isoformat()}."

    write_queue(queue)
    write_opportunities(rows)
    print(f"Promoted {len(chosen)} opportunities to {QUEUE_PATH}")
    for row in chosen:
        print(f"  {row['id']} -> {row['target_slug']}")
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    rows = load_opportunities()
    if args.status not in VALID_STATUSES:
        print(f"Invalid status: {args.status}", file=sys.stderr)
        return 1
    changed = 0
    today = date.today().isoformat()
    wanted = set(args.ids)
    for row in rows:
        if row["id"] in wanted or row["target_slug"] in wanted:
            row["status"] = args.status
            if args.status == "published" and not row.get("published_at"):
                row["published_at"] = today
            changed += 1
    write_opportunities(rows)
    print(f"Updated {changed} opportunities")
    return 0 if changed == len(wanted) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate").set_defaults(func=cmd_validate)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    sub.add_parser("dedupe").set_defaults(func=cmd_dedupe)

    p_next = sub.add_parser("next")
    p_next.add_argument("--limit", type=int, default=20)
    p_next.add_argument("--status", default="discovered")
    p_next.set_defaults(func=cmd_next)

    p_promote = sub.add_parser("promote")
    p_promote.add_argument("--limit", type=int, default=20)
    p_promote.add_argument("--min-priority", type=int)
    p_promote.set_defaults(func=cmd_promote)

    p_mark = sub.add_parser("mark")
    p_mark.add_argument("status")
    p_mark.add_argument("ids", nargs="+")
    p_mark.set_defaults(func=cmd_mark)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
