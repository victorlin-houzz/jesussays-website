"""Editorial quality rules shared by build and validation scripts.

These checks exist because the site once filled up with hundreds of templated,
keyword-swapped pages. They keep every Faith Library article specific, accurate
to the King James text, safe on sensitive topics, and consistent with how the
app is positioned (see ../quotebible/Documentation/APP_STORE_LISTING.md).
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kjv  # noqa: E402

# Product positioning: never describe the app with these (articles may still refer
# readers to counselors, doctors, and crisis lines; that is care guidance).
BANNED_PATTERNS = [
    (r"\bAI[- ](?:powered|bible|chat|companion|personali[sz]ed)\b", "AI-forward positioning"),
    (r"\bconfession journal", "unlisted app feature (confession journaling)"),
    (r"\bpersonali[sz]ed (?:bible )?verses?\b", "unlisted app claim (personalized verses)"),
    (r"\btalk to jesus\b", "implies Jesus speaks through the app"),
    (r"\bmanifest(?:ing|ation)\b|\bthe universe\b|\bvibrations?\b", "manifestation framing"),
    (r"\bresearch shows\b|\bstudies show\b", "unsupported research claim"),
    (r"\bin today's fast-paced world\b|\blet's dive in\b|\bin this article\b", "filler phrase"),
    (r"begins by bringing .{3,60} to God honestly", "retired template boilerplate"),
    (r"Most people do not need more religious pressure when they search for", "retired template boilerplate"),
]

SENSITIVE = {  # slug keyword -> required phrase(s) (any)
    "depression": ["988"], "hopeless": ["988"], "loss": ["988"], "lonel": ["988"], "healing": ["988", "doctor", "medical"],
    "anxiety": ["988", "counselor", "doctor"], "addiction": ["1-800-662-4357", "SAMHSA"],
    "relationships": ["1-800-799-7233"], "marriage": ["1-800-799-7233"], "forgiveness": ["1-800-799-7233", "unsafe", "danger"],
    "anger": ["1-800-799-7233", "unsafe", "danger"], "job-loss": ["988", "counselor"],
}

VERSE_ITEM = re.compile(r"<strong>\s*([1-3]?\s?[A-Z][A-Za-z ]+?\s\d+(?::\d+(?:[-–]\d+)?)?)[a-c]?\s*</strong>\s*(?:[—–-]|&mdash;)\s*[“\"](.+?)[”\"]", re.S)
VERSE_BLOCK = re.compile(r'<blockquote class="verse">\s*<p>(.*?)</p>\s*<cite>(.*?)</cite>', re.S)


def _norm(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", "", text)).lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


_BIBLE = None


def bible():
    global _BIBLE
    if _BIBLE is None and kjv.DEFAULT_BIBLE.exists():
        _BIBLE = kjv.load(kjv.DEFAULT_BIBLE)
    return _BIBLE


def check_quotes(body: str) -> list[str]:
    """Every quoted verse must be verbatim KJV (partial quotes and ellipses allowed)."""
    b = bible()
    if b is None:
        return []
    problems = []
    pairs = [(ref, quote) for ref, quote in VERSE_ITEM.findall(body)]
    pairs += [(strip_ref(cite), quote) for quote, cite in VERSE_BLOCK.findall(body)]
    for ref, quote in pairs:
        ref = strip_ref(ref)
        try:
            passage = _norm(kjv.lookup(b, ref))
        except ValueError as exc:
            problems.append(f"bad reference {ref!r}: {exc}")
            continue
        for segment in re.split(r"…|\.\.\.", quote):
            seg = _norm(segment)
            if seg and seg not in passage:
                problems.append(f"{ref}: quote is not verbatim KJV: “{strip(segment)[:70]}”")
                break
    return problems


_ALL_VERSES = None


def all_verses() -> list[str]:
    global _ALL_VERSES
    b = bible()
    if _ALL_VERSES is None and b is not None:
        _ALL_VERSES = [
            _norm(kjv.lookup(b, f"{name} {ci}:{vi}"))
            for name, chapters in b.items()
            for ci, ch in enumerate(chapters, start=1)
            for vi in range(1, len(ch) + 1)
        ]
    return _ALL_VERSES or []


def unmatched_inline_quotes(body: str, min_words: int = 6) -> list[str]:
    """Quoted phrases of 6+ words that appear nowhere in the KJV (review: paraphrase or other translation?)."""
    verses = all_verses()
    if not verses:
        return []
    joined = " ".join(verses)
    out = []
    for q in re.findall(r"[“](.+?)[”]", strip(re.sub(r'<div class="prayer">.*?</div>', "", body, flags=re.S))):
        for segment in re.split(r"…|\.\.\.", q):
            seg = _norm(segment)
            if len(seg.split()) >= min_words and seg not in joined:
                out.append(segment.strip()[:90])
                break
    return out


def strip_ref(ref: str) -> str:
    ref = strip(ref).replace("KJV", "").replace("(", "").replace(")", "").strip(" ,·")
    return re.sub(r"(\d)[a-c]\b", r"\1", ref)


def strip(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def check_body(slug: str, body: str, allowed_slugs: set[str]) -> list[str]:
    problems = []
    first = re.match(r"\s*<p>(.*?)</p>", body, re.S)
    if not first:
        problems.append("body must start with the direct-answer <p>")
    else:
        n = len(strip(first.group(1)).split())
        if not 25 <= n <= 80:
            problems.append(f"direct answer is {n} words (want 25–80)")
    faq = re.search(r'<section class="faq">(.*?)</section>\s*$', body, re.S)
    if not faq:
        problems.append("body must end with <section class=\"faq\">")
    else:
        count = len(re.findall(r"<h3", faq.group(1)))
        if not 3 <= count <= 7:
            problems.append(f"FAQ has {count} questions (want 4–6)")
    words = len(strip(body).split())
    if words < 500:
        problems.append(f"only {words} words")
    text = strip(body)
    for pattern, why in BANNED_PATTERNS:
        m = re.search(pattern, text, re.I)
        if m:
            problems.append(f"{why}: “{m.group(0)}”")
    for link in re.findall(r'href="/content/([^"#]+)\.html', body):
        if link not in allowed_slugs:
            problems.append(f"links to non-live article {link}")
    for key, needles in SENSITIVE.items():
        if key in slug and not any(n.lower() in text.lower() for n in needles):
            problems.append(f"sensitive topic ({key}) needs a care note mentioning one of {needles}")
    for tag in ("p", "li", "ul", "ol", "section", "aside", "blockquote", "div", "h2", "h3", "strong", "em", "table", "tr", "td", "th"):
        opens = len(re.findall(rf"<{tag}[\s>]", body))
        closes = len(re.findall(rf"</{tag}>", body))
        if opens != closes:
            problems.append(f"unbalanced <{tag}>: {opens} open vs {closes} close")
    if re.search(r'\sstyle="', body):
        problems.append("inline style attribute in body")
    problems += check_quotes(body)
    return problems


def shingles(text: str, k: int = 8) -> set[str]:
    words = _norm(text).split()
    return {" ".join(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def near_duplicates(bodies: dict[str, str], threshold: float = 0.2) -> list[str]:
    """Flag article pairs that share too many 8-word phrases (templated or copied text)."""
    sets = {slug: shingles(strip(b)) for slug, b in bodies.items()}
    slugs = sorted(sets)
    problems = []
    for i, a in enumerate(slugs):
        for b in slugs[i + 1:]:
            sa, sb = sets[a], sets[b]
            if not sa or not sb:
                continue
            overlap = len(sa & sb) / min(len(sa), len(sb))
            if overlap > threshold:
                problems.append(f"{a} and {b} share {overlap:.0%} of their 8-word phrases")
    return problems
