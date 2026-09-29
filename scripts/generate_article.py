#!/usr/bin/env python3
"""Draft one Faith Library article from the keyword queue for human review.

The model writes only the article body and catalog metadata, following
docs/editorial-guidelines.md. The draft is checked with the same rules as
scripts/check_aeo.py (verbatim KJV quotes, care notes, positioning, structure,
near-duplicate text); failures are sent back for one or two repair rounds.
A passing draft is added to _data/library.json and rendered with
scripts/build_site.py. Nothing is published until the change is reviewed and
merged through a pull request.

Usage:
  python3 scripts/generate_article.py                   # next pending keyword, local `claude` CLI
  python3 scripts/generate_article.py --backend api     # Anthropic API (ANTHROPIC_API_KEY)
  python3 scripts/generate_article.py --slug prayer-before-surgery-for-peace
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site  # noqa: E402
import content_rules  # noqa: E402
import kjv  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "content" / "queue.json"
GUIDELINES = ROOT / "docs" / "editorial-guidelines.md"
MODEL = "claude-opus-5-5"
MAX_REPAIRS = 2

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "h1": {"type": "string"},
        "description": {"type": "string"},
        "label": {"type": "string"},
        "category": {"type": "string"},
        "kind": {"type": "string"},
        "related": {"type": "array", "items": {"type": "string"}},
        "body_html": {"type": "string"},
    },
    "required": ["title", "h1", "description", "label", "category", "kind", "related", "body_html"],
    "additionalProperties": False,
}
KINDS = ["Bible Verses", "Prayer", "Devotional", "Christian Advice", "Jesus' Words", "Confession"]


def system_prompt(catalog: dict) -> str:
    """Stable across requests (guidelines + catalog), so it is cached."""
    cats = "\n".join(f"- {c['id']}: {c['name']}" for c in catalog["categories"] if c["id"] != "compare")
    live = "\n".join(f"- {a['slug']}: {a['h1']}" for a in catalog["articles"])
    return f"""You write articles for the Jesus Says Faith Library (jesussays.app), the website of the iPhone and iPad
app "Jesus Says: Daily Reflection". Follow these editorial guidelines exactly:

{GUIDELINES.read_text(encoding="utf-8")}

Categories (use one id for "category"):
{cats}

Allowed values for "kind": {", ".join(KINDS)}.

Live articles (the only pages you may link to or list in "related"; never duplicate one of these):
{live}

Respond with a single JSON object with the keys title, h1, description, label, category, kind, related (exactly
three live slugs), and body_html (the body fragment described in the guidelines). Quote Scripture only from the
King James Version, word for word."""


def call_api(system: str, messages: list[dict]) -> str:
    import anthropic

    client = anthropic.Anthropic()
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=32000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
    ) as stream:
        response = stream.get_final_message()
    if response.stop_reason == "refusal":
        raise RuntimeError(f"model declined: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("draft hit max_tokens")
    return next(block.text for block in response.content if block.type == "text")


def call_cli(system: str, messages: list[dict]) -> str:
    transcript = "\n\n".join(f"[{m['role'].upper()}]\n{m['content']}" for m in messages)
    prompt = f"{system}\n\n{transcript}\n\nReply with the JSON object only, no code fences."
    result = subprocess.run(["claude", "-p", prompt, "--allowedTools", ""], capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr[:500]}")
    return result.stdout


def parse_draft(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start:end + 1])


def review(draft: dict, slug: str, catalog: dict) -> list[str]:
    live = {a["slug"] for a in catalog["articles"]}
    cats = {c["id"] for c in catalog["categories"]}
    body = draft.get("body_html", "").strip()
    problems = content_rules.check_body(slug, body, live)
    if draft.get("category") not in cats or draft.get("category") == "compare":
        problems.append(f"category must be one of {sorted(cats - {'compare'})}")
    if draft.get("kind") not in KINDS:
        problems.append(f"kind must be one of {KINDS}")
    related = draft.get("related", [])
    if len(related) != 3 or any(r not in live for r in related):
        problems.append("related must list exactly three live slugs")
    if not 120 <= len(draft.get("description", "")) <= 165:
        problems.append("description must be 140–160 characters")
    if len(draft.get("title", "")) > 60:
        problems.append("title must be 60 characters or fewer")
    bodies = {a["slug"]: build_site.extract_body((ROOT / "content" / f"{a['slug']}.html").read_text(encoding="utf-8"))
              for a in catalog["articles"]}
    bodies[slug] = body
    problems += [p for p in content_rules.near_duplicates(bodies) if slug in p]
    return problems


def kjv_help(problems: list[str]) -> str:
    """Exact KJV text for every reference the checker flagged, so the repair round can quote it verbatim."""
    bible = content_rules.bible()
    refs = sorted({m.group(1) for p in problems if (m := re.match(r"(.+?): quote is not verbatim KJV", p))})
    if not bible or not refs:
        return ""
    lines = []
    for ref in refs:
        try:
            lines.append(f"{ref} (KJV): {kjv.lookup(bible, ref)}")
        except ValueError:
            pass
    return "\n\nExact KJV text for the flagged references:\n" + "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backend", choices=["cli", "api"], default="cli")
    ap.add_argument("--slug", help="queue slug to draft instead of the next pending one")
    args = ap.parse_args()

    if content_rules.bible() is None:
        print(f"KJV Bible not found at {kjv.DEFAULT_BIBLE}; set KJV_BIBLE_PATH. Refusing to draft unverifiable quotes.")
        return 2

    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    item = next((q for q in queue if q["slug"] == args.slug), None) if args.slug else \
        next((q for q in queue if q.get("status") == "pending"), None)
    if item is None:
        print("Nothing to draft: no matching pending keyword.")
        return 0
    slug, keyword = item["slug"], item["keyword"]
    catalog = build_site.load_catalog()
    redirects = json.loads(build_site.REDIRECTS.read_text(encoding="utf-8"))
    if slug in {a["slug"] for a in catalog["articles"]} or slug in redirects:
        print(f"{slug} already exists or is a retired URL; pick another keyword.")
        return 1

    system = system_prompt(catalog)
    call = call_api if args.backend == "api" else call_cli
    messages = [{"role": "user", "content": f'Write the article for the search query "{keyword}" (slug: {slug}).'}]
    draft, problems = {}, ["no draft"]
    for attempt in range(1 + MAX_REPAIRS):
        raw = call(system, messages)
        try:
            draft = parse_draft(raw)
            problems = review(draft, slug, catalog)
        except (ValueError, json.JSONDecodeError) as exc:
            problems = [f"output was not valid JSON: {exc}"]
        print(f"attempt {attempt + 1}: {len(problems)} problem(s)")
        if not problems:
            break
        messages += [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "Fix these problems and return the complete corrected JSON object:\n- "
             + "\n- ".join(problems) + kjv_help(problems)},
        ]
    if problems:
        print("Draft still fails review; nothing written:")
        for p in problems:
            print(f"  • {p}")
        return 1

    today = date.today().isoformat()
    catalog["articles"].append({
        "slug": slug, "category": draft["category"], "kind": draft["kind"], "title": draft["title"].strip(),
        "h1": draft["h1"].strip(), "description": draft["description"].strip(), "label": draft["label"].strip(),
        "published": today, "modified": today, "related": draft["related"],
    })
    build_site.CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    page = ROOT / "content" / f"{slug}.html"
    page.write_text(f"{build_site.BODY_START}\n{draft['body_html'].strip()}\n{build_site.BODY_END}\n", encoding="utf-8")
    item.update(status="published", published_date=today)
    QUEUE_PATH.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    if build_site.build() != 0:
        return 1
    print(f"Drafted content/{slug}.html. Read it, then open a pull request for review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
