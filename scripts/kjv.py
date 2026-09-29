#!/usr/bin/env python3
"""Print exact KJV text for Scripture references, using the app's bundled Bible.

Usage:
  python3 scripts/kjv.py "John 14:27" "Philippians 4:6-7" "Psalm 23"
  python3 scripts/kjv.py --bible ../quotebible/assets/bible/kjv.json "1 Peter 5:7"

Articles quote the King James Version so the website matches the app's reader.
Words the KJV translators supplied (marked {like this} in the source) are
printed without the braces; margin notes ({word: Heb. ...}) are dropped.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# The app repo is expected next to this one; CI can point KJV_BIBLE_PATH elsewhere.
DEFAULT_BIBLE = Path(os.environ.get("KJV_BIBLE_PATH") or
                     Path(__file__).resolve().parents[1].parent / "quotebible" / "assets" / "bible" / "kjv.json")

ALIASES = {
    "psalm": "Psalms",
    "psalms": "Psalms",
    "song of songs": "Song of Solomon",
    "revelations": "Revelation",
}

REF = re.compile(r"^\s*(?P<book>(?:[1-3]\s)?[A-Za-z][A-Za-z ]*?)\s+(?P<ch>\d+)(?::(?P<v1>\d+)(?:[-–](?P<v2>\d+))?)?\s*$")


def load(path: Path) -> dict[str, list[list[str]]]:
    books = json.loads(path.read_text(encoding="utf-8-sig"))
    return {b["name"].lower(): b["chapters"] for b in books}


def lookup(bible: dict[str, list[list[str]]], ref: str) -> str:
    m = REF.match(ref)
    if not m:
        raise ValueError(f"unrecognised reference: {ref!r}")
    book = m["book"].strip()
    name = ALIASES.get(book.lower(), book).lower()
    if name not in bible:
        raise ValueError(f"unknown book: {book!r}")
    chapters = bible[name]
    ch = int(m["ch"])
    if not 1 <= ch <= len(chapters):
        raise ValueError(f"{book} has {len(chapters)} chapters")
    verses = chapters[ch - 1]
    v1 = int(m["v1"]) if m["v1"] else 1
    v2 = int(m["v2"]) if m["v2"] else (v1 if m["v1"] else len(verses))
    if not (1 <= v1 <= v2 <= len(verses)):
        raise ValueError(f"{book} {ch} has {len(verses)} verses")
    text = " ".join(verses[v1 - 1 : v2])
    text = re.sub(r"\s*\{[^{}]*:[^{}]*\}", "", text)  # translators' margin notes
    text = re.sub(r"^\[[^\]]*\]\s*", "", text)  # psalm superscriptions ("[A Psalm of David.]")
    return re.sub(r"\s+", " ", re.sub(r"[{}]", "", text)).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("refs", nargs="+")
    parser.add_argument("--bible", type=Path, default=DEFAULT_BIBLE)
    args = parser.parse_args()
    if not args.bible.exists():
        print(f"Bible JSON not found: {args.bible}", file=sys.stderr)
        return 2
    bible = load(args.bible)
    status = 0
    for ref in args.refs:
        try:
            print(f"{ref} (KJV): {lookup(bible, ref)}")
        except ValueError as exc:
            print(f"{ref}: ERROR {exc}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
