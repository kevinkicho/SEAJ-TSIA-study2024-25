#!/usr/bin/env python3.12
"""Apply triage corrections, dedup by md5, move PDFs into bucket folders,
and update source_file references in the main graph.

Idempotent: safe to rerun. Records all moves to triage_applied.json.

Cleanup policy (Option A): only nodes/edges whose source_file resolves to
a file in `unrelated/` are dropped from the main graph. Brochures, datasheets,
specs, and IR decks remain — they contributed real qualitative content.
"""
from __future__ import annotations
import hashlib, json, shutil, sys
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"
TRIAGE_PATH = GF / "triage.json"
OUT_PATH = GF / "triage_applied.json"

BUCKETS = ["annual_reports", "quarterly_reports", "investor_presentations",
           "brochures", "industry_reports", "unrelated"]

# Manual corrections to apply on top of triage.json
RECLASSIFICATIONS = {
    "annual-report-2024-asm-final.pdf":      "annual_reports",     # was industry_reports
    "FUJI_ELECTRIC_ar2025_02_02_e.pdf":      "brochures",          # 1-page fragment
    "FUJI_ELECTRIC_ar2025_02_04_e.pdf":      "brochures",          # 1-page fragment
    "ALCOR fabless 2024_AnnualReport_EN.pdf": "unrelated",         # md5 dup of already-processed alcor
}

# The 10 already-processed PDFs go straight to annual_reports/
ALREADY_PROCESSED = [
    "2024 Annual Report-E TSMC.pdf",
    "2024_WPG_annual_report_E.pdf",
    "2024AR_ENG_all UMC United Microelectronics Corporation Annual report 2024.pdf",
    "2025 Annual Report (Bookmarked) APPLIED MATERIALS.pdf",
    "00 MEDIPAL integrated report 2025.pdf",
    "2024_AnnualReport_EN.pdf",
    "2024_Annual Report ITRI taiwan.pdf",
    "20250603150724453273521_en ASE holdings annual report 2024.pdf",
    "20250506232053383995188_en VIS annual report 2025.pdf",
    "EGIS annual report 2024 神盾113年報-EN-上傳版-1.pdf",
]


def md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    triage = json.loads(TRIAGE_PATH.read_text())

    # Build flat assignment dict: filename -> bucket
    assignments: dict[str, str] = {}
    for bucket, items in triage["buckets"].items():
        for it in items:
            assignments[it["filename"]] = bucket
    # Also fold in the 10 already-processed
    for fn in ALREADY_PROCESSED:
        assignments[fn] = "annual_reports"
    # Apply corrections
    for fn, bucket in RECLASSIFICATIONS.items():
        if fn in assignments:
            assignments[fn] = bucket

    # Create bucket dirs
    for b in BUCKETS:
        (ROOT / b).mkdir(exist_ok=True)

    # Compute md5 for every PDF (root + already in bucket dirs)
    pdfs_in_root = list(ROOT.glob("*.pdf"))
    pdfs_in_buckets = [p for b in BUCKETS for p in (ROOT / b).glob("*.pdf")]
    all_pdfs = pdfs_in_root + pdfs_in_buckets

    # md5 map: hash -> [paths]
    md5_map: dict[str, list[Path]] = {}
    for p in all_pdfs:
        h = md5(p)
        md5_map.setdefault(h, []).append(p)

    moves: list[dict] = []
    skipped: list[dict] = []
    duplicates_dropped: list[dict] = []

    for p in pdfs_in_root:
        bucket = assignments.get(p.name)
        if bucket is None:
            skipped.append({"filename": p.name, "reason": "not in triage assignments"})
            continue
        target_dir = ROOT / bucket
        target = target_dir / p.name
        # Already there?
        if target.exists():
            skipped.append({"filename": p.name, "reason": f"already in {bucket}/"})
            continue
        # md5 dup of file already in target bucket?
        h = md5(p)
        same_hash = [q for q in md5_map[h] if q != p]
        if same_hash:
            in_bucket = [q for q in same_hash if q.parent.name in BUCKETS]
            if in_bucket:
                # An identical file is already in a bucket → drop the source file
                p.unlink()
                duplicates_dropped.append({
                    "filename": p.name, "md5": h,
                    "kept": str(in_bucket[0].relative_to(ROOT)),
                })
                continue
        # Move
        shutil.move(str(p), str(target))
        moves.append({
            "filename": p.name, "bucket": bucket,
            "from": str(p.relative_to(ROOT)),
            "to": str(target.relative_to(ROOT)),
        })

    # Now patch the main graph: only purge nodes whose source_file is in unrelated/
    main_graph_path = ROOT / "graphify-out" / "graph.json"
    graph_changes = {"nodes_removed": 0, "edges_removed": 0,
                     "source_files_updated": 0}
    unrelated_filenames = {fn for fn, b in assignments.items() if b == "unrelated"}

    if main_graph_path.exists():
        g = json.loads(main_graph_path.read_text())
        nodes = g.get("nodes", [])
        edges = g.get("links") or g.get("edges") or []

        # Identify nodes to drop (source_file matches an unrelated PDF)
        drop_node_ids = set()
        for n in nodes:
            sf = (n.get("source_file") or "").strip()
            # extract just filename
            sf_name = Path(sf).name if sf else ""
            if sf_name in unrelated_filenames:
                drop_node_ids.add(n["id"])

        if drop_node_ids:
            # Filter nodes
            kept_nodes = [n for n in nodes if n["id"] not in drop_node_ids]
            kept_edges = [e for e in edges
                          if e.get("source") not in drop_node_ids
                          and e.get("target") not in drop_node_ids]
            graph_changes["nodes_removed"] = len(nodes) - len(kept_nodes)
            graph_changes["edges_removed"] = len(edges) - len(kept_edges)
            g["nodes"] = kept_nodes
            if "links" in g:
                g["links"] = kept_edges
            elif "edges" in g:
                g["edges"] = kept_edges

        # Update source_file paths to bucket-prefixed paths for moved files.
        # (Brochures/IR decks/quarterly etc. still reference the now-moved files.)
        for n in g["nodes"]:
            sf = (n.get("source_file") or "").strip()
            if not sf:
                continue
            sf_name = Path(sf).name
            bucket = assignments.get(sf_name)
            if bucket and not sf.startswith(f"{bucket}/"):
                # Update only if file actually exists in the bucket now
                if (ROOT / bucket / sf_name).exists():
                    n["source_file"] = f"{bucket}/{sf_name}"
                    graph_changes["source_files_updated"] += 1

        # Backup before writing
        backup = main_graph_path.with_suffix(".json.pre-triage-bak")
        if not backup.exists():
            backup.write_text(json.dumps(json.loads(main_graph_path.read_text()), ensure_ascii=False))
        main_graph_path.write_text(json.dumps(g, indent=2, ensure_ascii=False))

    # Update extraction JSONs' source_pdf field for the 10 already-processed
    KEY_TO_PDF = {
        "tsmc":    "2024 Annual Report-E TSMC.pdf",
        "wpg":     "2024_WPG_annual_report_E.pdf",
        "umc":     "2024AR_ENG_all UMC United Microelectronics Corporation Annual report 2024.pdf",
        "amat":    "2025 Annual Report (Bookmarked) APPLIED MATERIALS.pdf",
        "medipal": "00 MEDIPAL integrated report 2025.pdf",
        "alcor":   "2024_AnnualReport_EN.pdf",
        "itri":    "2024_Annual Report ITRI taiwan.pdf",
        "ase":     "20250603150724453273521_en ASE holdings annual report 2024.pdf",
        "vis":     "20250506232053383995188_en VIS annual report 2025.pdf",
        "egis":    "EGIS annual report 2024 神盾113年報-EN-上傳版-1.pdf",
    }
    extraction_updates = []
    for key, fname in KEY_TO_PDF.items():
        if key == "tsmc":
            for sub in ("tsmc_financials.json", "tsmc_people.json"):
                p = GF / "tsmc" / sub
                if p.exists():
                    j = json.loads(p.read_text())
                    if j.get("source_pdf") == fname:
                        j["source_pdf"] = f"annual_reports/{fname}"
                        p.write_text(json.dumps(j, indent=2, ensure_ascii=False))
                        extraction_updates.append(str(p.relative_to(ROOT)))
            continue
        ext = GF / key / f"{key}_extraction.json"
        if ext.exists():
            j = json.loads(ext.read_text())
            sp = j.get("source_pdf") or j.get("source")
            if sp == fname:
                j["source_pdf"] = f"annual_reports/{fname}"
                ext.write_text(json.dumps(j, indent=2, ensure_ascii=False))
                extraction_updates.append(str(ext.relative_to(ROOT)))

    # Write report
    report = {
        "moves": moves,
        "skipped": skipped,
        "duplicates_dropped": duplicates_dropped,
        "graph_changes": graph_changes,
        "graph_unrelated_filenames": sorted(unrelated_filenames),
        "extraction_updates": extraction_updates,
        "final_bucket_counts": {
            b: sum(1 for fn, bb in assignments.items() if bb == b)
            for b in BUCKETS
        },
    }
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_PATH}")
    print(f"  Moves: {len(moves)}")
    print(f"  Duplicates dropped: {len(duplicates_dropped)}")
    print(f"  Skipped: {len(skipped)}")
    print(f"  Graph: removed {graph_changes['nodes_removed']} nodes, "
          f"{graph_changes['edges_removed']} edges; "
          f"updated {graph_changes['source_files_updated']} source_file paths")
    print(f"  Extraction JSONs updated: {len(extraction_updates)}")
    print(f"\nFinal bucket counts:")
    for b, n in report["final_bucket_counts"].items():
        print(f"  {b:25s}: {n}")


if __name__ == "__main__":
    main()
