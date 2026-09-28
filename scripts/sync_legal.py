#!/usr/bin/env python3
"""Copy approved app legal Markdown and render the website's permanent URLs."""
from pathlib import Path
import argparse
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('app_repo', type=Path, help='Path to the quotebible repository')
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
for name, title in [('privacy_policy', 'Privacy Policy'), ('terms_of_use', 'Terms of Use')]:
    source = args.app_repo / 'assets' / f'{name}.md'
    rendered = subprocess.check_output([
        'pandoc', str(source), '--from=gfm', '--to=html5', '--standalone',
        f'--template={args.app_repo / "tools/legal-template.html"}',
        '--metadata', f'title={title} - Jesus Says',
    ], text=True)
    rendered = rendered.replace('</head>', f'<link rel="canonical" href="https://jesussays.app/{name}.html" />\n<meta name="description" content="{title} for Jesus Says. Read how the app works and how to contact us." />\n</head>')
    rendered = rendered.replace('<main>', '<main>\n<nav aria-label="Legal navigation"><a href="/">Jesus Says home</a> · <a href="/privacy_policy.html">Privacy Policy</a> · <a href="/terms_of_use.html">Terms of Use</a></nav>')
    shutil.copyfile(source, root / f'{name}.md')
    (root / f'{name}.html').write_text(rendered)
    print(f'Updated https://jesussays.app/{name}.html')
