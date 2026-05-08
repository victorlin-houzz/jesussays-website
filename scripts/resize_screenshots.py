#!/usr/bin/env python3
"""Resize App Store screenshots to web size (max height 800px)."""
from pathlib import Path
from PIL import Image

src = Path.home() / "Desktop/jesussays_appstore_submission/submission_2026_04_28/iphone_1290x2796"
dst = Path("assets/screenshots")
dst.mkdir(parents=True, exist_ok=True)

pngs = sorted(src.glob("*.png"))
assert len(pngs) == 6, f"Expected 6 screenshots, found {len(pngs)}"

for i, png in enumerate(pngs, 1):
    img = Image.open(png)
    w, h = img.size
    new_h = 800
    new_w = round(w * new_h / h)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    out = dst / f"screenshot-{i:02d}.png"
    img.save(out, optimize=True)
    size_kb = out.stat().st_size // 1024
    print(f"screenshot-{i:02d}.png  {new_w}×{new_h}  {size_kb}KB")

print(f"\nSaved {len(pngs)} screenshots to {dst}/")
