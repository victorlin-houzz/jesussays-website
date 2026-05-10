#!/usr/bin/env python3
"""Generate and apply GPT-written intro paragraphs to existing Jesus Says articles."""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CONTENT_DIR = Path("content")
SKIP = {"index.html", "keyword-clusters.html"}
PROMPT = (
    'Write me an intro for this piece of content that answers the question in the first sentence. '
    'If not possible write me a tldr.'
)
INTRO_INSTRUCTIONS = f"""You are editing a Christian SEO article. Use this prompt exactly against the article below: \"{PROMPT}\"

Rules:
- Return JSON only matching schema {{"intro": string}}
- Write exactly one paragraph, 35-75 words
- The first sentence must directly answer the article's main question if possible
- If the article does not contain a clear question, return a TLDR instead
- No markdown, no labels, no quotes around the paragraph
- Keep the tone warm, clear, Christian, and non-preachy
"""
SCHEMA = {
    "type": "object",
    "properties": {"intro": {"type": "string"}},
    "required": ["intro"],
    "additionalProperties": False,
}


def article_paths() -> list[Path]:
    return sorted(p for p in CONTENT_DIR.glob("*.html") if p.name not in SKIP)


def extract_article_text(page: Path) -> str:
    text = page.read_text(encoding="utf-8")
    main_match = re.search(r'<div class="art-page">(.*?)<section class="app-cta">', text, re.S)
    body = main_match.group(1) if main_match else text
    body = re.sub(r"<svg.*?</svg>", " ", body, flags=re.S)
    body = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
    body = re.sub(r"<style.*?</style>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "\n", body)
    body = html.unescape(body)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    return "\n".join(lines)


def build_prompt(page: Path) -> str:
    article_text = extract_article_text(page)
    return f"{INTRO_INSTRUCTIONS}\nARTICLE ({page.name}):\n{article_text[:7000]}"


def generate_intro(page: Path) -> str:
    prompt = build_prompt(page)
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        prompt_path = td_path / "prompt.txt"
        schema_path = td_path / "schema.json"
        out_path = td_path / "last_message.json"
        prompt_path.write_text(prompt, encoding="utf-8")
        schema_path.write_text(json.dumps(SCHEMA), encoding="utf-8")

        result = subprocess.run(
            [
                "codex",
                "exec",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--output-last-message",
                str(out_path),
                "--output-schema",
                str(schema_path),
                "-C",
                str(Path.cwd()),
                "-",
            ],
            stdin=prompt_path.open("r", encoding="utf-8"),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"codex exec failed for {page.name}:\nSTDOUT:\n{result.stdout[-1000:]}\nSTDERR:\n{result.stderr[-2000:]}"
            )
        payload = json.loads(out_path.read_text(encoding="utf-8"))
        intro = payload["intro"].strip()
        if not intro:
            raise RuntimeError(f"Empty intro returned for {page.name}")
        return intro


def apply_intro(page: Path, intro: str) -> None:
    original = page.read_text(encoding="utf-8")
    escaped_intro = html.escape(intro, quote=False)
    pattern = r'(<h1>.*?</h1>\s*<p>)(.*?)(</p>)'
    updated, count = re.subn(pattern, rf'\1{escaped_intro}\3', original, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Could not replace intro paragraph in {page.name}")
    page.write_text(updated, encoding="utf-8")


def main() -> None:
    pages = article_paths()
    target_names = set(sys.argv[1:])
    if target_names:
        pages = [p for p in pages if p.name in target_names or p.stem in target_names]
        missing = sorted(target_names - {p.name for p in pages} - {p.stem for p in pages})
        if missing:
            raise SystemExit(f"Unknown page(s): {', '.join(missing)}")

    print(f"Processing {len(pages)} article(s)...")
    generated: dict[str, str] = {}
    for idx, page in enumerate(pages, start=1):
        print(f"[{idx}/{len(pages)}] Generating intro for {page.name}...", flush=True)
        intro = generate_intro(page)
        apply_intro(page, intro)
        generated[page.name] = intro
        print(f"[{idx}/{len(pages)}] Updated {page.name}", flush=True)

    audit_path = CONTENT_DIR / "article-intros.generated.json"
    audit_path.write_text(json.dumps(generated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Done. Wrote audit file to {audit_path}")


if __name__ == "__main__":
    main()
