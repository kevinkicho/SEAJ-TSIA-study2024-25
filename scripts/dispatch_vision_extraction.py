#!/usr/bin/env python3.12
"""Build per-batch dispatch payloads for vision extraction.

Reads bulk_rasterize_summary.json, splits companies into N batches,
writes one JSON manifest per batch. Each manifest is the input the
parent session passes to a subagent.

Usage:
    python3.12 scripts/dispatch_vision_extraction.py --batches 9
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=int, default=9)
    ap.add_argument("--out-dir", default=str(GF / "vision_batches"))
    args = ap.parse_args()

    summary = json.loads((GF / "bulk_rasterize_summary.json").read_text())
    # Skip companies that already have an extraction file
    pending = {}
    for key, info in summary.items():
        if not info.get("pages"):
            continue
        existing = GF / key / f"{key}_extraction.json"
        if existing.exists():
            continue
        pending[key] = info

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    keys = sorted(pending.keys())

    # Round-robin distribute so batches end up balanced even if some
    # companies have many more pages than others.
    batches: list[list[str]] = [[] for _ in range(args.batches)]
    pages_per_batch = [0] * args.batches
    # Sort keys by descending page count so we pack heavy ones first
    keys_sorted = sorted(keys, key=lambda k: -len(pending[k]["pages"]))
    for k in keys_sorted:
        # Pick batch with smallest current page count
        idx = pages_per_batch.index(min(pages_per_batch))
        batches[idx].append(k)
        pages_per_batch[idx] += len(pending[k]["pages"])

    manifests = []
    for i, keys_in_batch in enumerate(batches, start=1):
        if not keys_in_batch:
            continue
        manifest = {
            "batch_id": i,
            "total_batches": args.batches,
            "companies": [],
        }
        for k in keys_in_batch:
            info = pending[k]
            manifest["companies"].append({
                "key": k,
                "bucket": info["bucket"],
                "source_pdf": info["source_pdf"],
                "total_pages": info["total_pages"],
                "pages": info["pages"],  # [{page, role, png}, ...]
                "output_json": f"graphify-financial/{k}/{k}_extraction.json",
                "pages_dir": f"graphify-financial/{k}/pages/",
            })
        path = out_dir / f"batch_{i:02d}.json"
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        manifests.append({"batch_id": i, "path": str(path), "n_companies": len(keys_in_batch),
                          "n_pages": pages_per_batch[i-1]})

    print(f"Wrote {len(manifests)} batch manifests to {out_dir}/")
    for m in manifests:
        print(f"  batch {m['batch_id']:2d}: {m['n_companies']:2d} companies, {m['n_pages']:3d} pages")
    print(f"\nTotal pending companies: {len(pending)}")
    print(f"Total pending pages: {sum(pages_per_batch)}")


if __name__ == "__main__":
    main()
