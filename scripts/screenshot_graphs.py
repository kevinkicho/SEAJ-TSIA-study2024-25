#!/usr/bin/env python3.12
"""Take 4 screenshots (2D + 3D, main + financial) and compose a 2x2 grid.

Output:
  docs/img/graphs_overview.png  (composite, ~1.5 MB)
  docs/img/graph_main_2d.png
  docs/img/graph_main_3d.png
  docs/img/graph_financial_2d.png
  docs/img/graph_financial_3d.png
"""
from __future__ import annotations
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
OUT_DIR = ROOT / "docs" / "img"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORT = {"width": 1600, "height": 1000}
SHOTS = [
    {
        # graph-3d.html defaults to 3D, so click btn2d to switch
        "name": "main_2d",
        "url": (ROOT / "graphify-out/graph-3d.html").as_uri(),
        "click": "#btn2d",
        "settle_ms": 9000,
        "label": "Main qualitative graph — 2D (1,512 nodes)",
    },
    {
        "name": "main_3d",
        "url": (ROOT / "graphify-out/graph-3d.html").as_uri(),
        "click": None,
        "settle_ms": 10000,
        "label": "Main qualitative graph — 3D",
    },
    {
        "name": "financial_2d",
        "url": (ROOT / "graphify-financial/graph-financial.html").as_uri(),
        "click": None,
        "settle_ms": 8000,
        "label": "Financial subgraph — 2D (82 companies / 714 people)",
    },
    {
        "name": "financial_3d",
        "url": (ROOT / "graphify-financial/graph-financial.html").as_uri(),
        "click": "#btn3d",
        "settle_ms": 9000,
        "label": "Financial subgraph — 3D",
    },
    {
        # NEW — financial-briefs subgraph (deterministic parser of natural-prose briefs)
        "name": "briefs",
        "url": (ROOT / "financial_briefs/graphify-out/graph.html").as_uri(),
        "click": None,
        "settle_ms": 8000,
        "label": "Financial-briefs subgraph (572 nodes from 82 prose briefs)",
    },
    {
        # NEW — integrated company explorer (tabular per-company)
        "name": "integrated",
        "url": (ROOT / "graphify-financial/graph-integrated.html").as_uri(),
        "click": None,
        "settle_ms": 5000,
        "label": "Integrated company explorer (per-company financials + structure)",
    },
]


def capture_one(page, shot: dict) -> Path:
    print(f"  → {shot['name']}: navigating")
    page.goto(shot["url"], wait_until="networkidle", timeout=60000)
    sel = shot.get("click")
    if sel:
        try:
            # Use no_wait_after — these toggles don't navigate, they just swap divs
            page.locator(sel).click(no_wait_after=True, timeout=5000)
            print(f"     clicked {sel}")
        except Exception as e:
            print(f"     [warn] could not click {sel}: {e}")
    # Wait for graph stabilization (force-directed simulation needs time to settle)
    page.wait_for_timeout(shot["settle_ms"])
    out = OUT_DIR / f"graph_{shot['name']}.png"
    page.screenshot(path=str(out), full_page=False)
    print(f"     saved {out.relative_to(ROOT)} ({out.stat().st_size//1024} KB)")
    return out


def main():
    paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
        ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = ctx.new_page()
        for shot in SHOTS:
            path = capture_one(page, shot)
            paths.append((path, shot["label"]))
        browser.close()

    # Compose 2x3 grid (6 panels: main 2D/3D, financial 2D/3D, briefs, integrated)
    print("\n[compose] building 2x3 grid")
    target_w, target_h = 900, 565  # cell size; final ~1800×1755
    cols, rows = 2, 3
    grid = Image.new("RGB", (target_w * cols, target_h * rows + 60), color="#0b1220")
    draw = ImageDraw.Draw(grid)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    header = "SEAJ TSIA — Knowledge Graph Visualizations"
    draw.text((20, 18), header, fill="#93c5fd", font=font)
    draw.text((20, 42), "Main qualitative graph + financial subgraph + brief-derived enrichment + per-company explorer",
              fill="#6b7280", font=font_small)

    for i, (path, label) in enumerate(paths):
        col, row = i % cols, i // cols
        x, y = col * target_w, 60 + row * target_h
        img = Image.open(path).resize((target_w, target_h), Image.LANCZOS)
        grid.paste(img, (x, y))
        draw.rectangle([x, y + target_h - 26, x + target_w, y + target_h],
                       fill="#111827")
        draw.text((x + 12, y + target_h - 21), label, fill="#dbeafe", font=font_small)

    composite = OUT_DIR / "graphs_overview.png"
    grid.save(composite, optimize=True)
    print(f"[done] composite: {composite.relative_to(ROOT)} ({composite.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
