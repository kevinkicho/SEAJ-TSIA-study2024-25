#!/usr/bin/env python3.12
"""Downscale all PNGs in graphify-financial/<key>/pages/ to fit within 1800x1800.

The Anthropic vision API rejects multi-image requests when any image
exceeds 2000px on the long edge. pdftoppm @ 200 DPI produced 3308×2339
PNGs — too large. Downscaling to ≤1800 keeps detail but stays well under
the limit for parallel processing.

Idempotent: skips PNGs already <= 1800px.
"""
from __future__ import annotations
import multiprocessing
from pathlib import Path
from PIL import Image

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"
MAX_DIM = 1800


def downscale(p: Path) -> tuple[str, str]:
    try:
        img = Image.open(p)
        w, h = img.size
        if max(w, h) <= MAX_DIM:
            return (str(p.name), "skip")
        # Compute new size preserving aspect
        if w >= h:
            new_w = MAX_DIM
            new_h = int(h * MAX_DIM / w)
        else:
            new_h = MAX_DIM
            new_w = int(w * MAX_DIM / h)
        img2 = img.resize((new_w, new_h), Image.LANCZOS)
        img2.save(p, optimize=True)
        return (str(p.name), f"resized {w}x{h} -> {new_w}x{new_h}")
    except Exception as e:
        return (str(p.name), f"FAIL: {e}")


def main():
    pngs = sorted(GF.glob("*/pages/*.png"))
    if not pngs:
        print("No PNGs found")
        return
    print(f"Scanning {len(pngs)} PNGs...")
    n_skip = n_resize = n_fail = 0
    with multiprocessing.Pool(8) as pool:
        for name, status in pool.imap_unordered(downscale, pngs):
            if status == "skip":
                n_skip += 1
            elif status.startswith("FAIL"):
                n_fail += 1
                print(f"  FAIL: {name}: {status}")
            else:
                n_resize += 1
    print(f"\nResized: {n_resize}")
    print(f"Skipped (already small): {n_skip}")
    print(f"Failed: {n_fail}")


if __name__ == "__main__":
    main()
