"""Keep the shared HeyCatch client entry in every published HTML page."""
from pathlib import Path
import argparse

SCRIPT = '<script type="module" src="/assets/analytics.js"></script>'
ROOT = Path(__file__).resolve().parent.parent


def with_analytics(html: str) -> str:
    if SCRIPT in html:
        return html
    if '</head>' not in html:
        raise ValueError('Cannot add analytics: HTML has no closing head tag')
    return html.replace('</head>', f'{SCRIPT}\n</head>', 1)


def site_pages():
    yield from sorted(ROOT.glob('*.html'))
    yield from sorted((ROOT / 'content').rglob('*.html'))
    yield from sorted((ROOT / 'play').rglob('*.html'))
    yield from sorted((ROOT / 'author').rglob('*.html'))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if any page lacks exactly one analytics entry in its head')
    args = parser.parse_args()
    pages = list(site_pages())
    missing = []
    for page in pages:
        html = page.read_text(encoding='utf-8')
        if args.check:
            head = html.partition('</head>')[0]
            if html.count(SCRIPT) != 1 or SCRIPT not in head:
                missing.append(str(page.relative_to(ROOT)))
        else:
            updated = with_analytics(html)
            if updated != html:
                page.write_text(updated, encoding='utf-8')
    if missing:
        print('Missing or duplicate analytics entry: ' + ', '.join(missing))
        return 1
    print(f'Analytics {"checked" if args.check else "synchronized"}: {len(pages)} pages')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
