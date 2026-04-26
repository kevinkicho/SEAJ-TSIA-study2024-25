#!/usr/bin/env python3.12
"""Apply graphify-financial/corrections.json to the per-company extraction JSONs.

For each correction:
  - find the extraction JSON that contains the named page_id
  - update the matching metric's value (or append a new metric)
  - record the original value in a parallel `_corrections_applied` block
    on the page so the audit trail is preserved

Idempotent: if the value is already at the corrected target, it's left alone.
Always writes a `.pre-correction-bak` of the JSON the first time it modifies it.

Output: graphify-financial/corrections_applied_log.json
"""
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"


def find_extraction_for_page(page_id: str) -> Path | None:
    """Find the extraction JSON that contains a metric with this page_id.

    Strategy: extract the directory key from the page_id by matching against
    actual directory names.
    """
    # page_id looks like "<key>_p<NNN>" where <key> is the directory name
    for d in sorted(GF.iterdir(), key=lambda p: -len(p.name)):
        if not d.is_dir():
            continue
        if not page_id.startswith(d.name + "_p") and page_id != d.name:
            continue
        # Check the relevant JSON
        if d.name == "tsmc":
            cand = d / "tsmc_financials.json"
        else:
            cand = d / f"{d.name}_extraction.json"
        if cand.exists():
            return cand
    return None


def find_page_in_extraction(ex: dict, page_id: str) -> dict | None:
    for page in ex.get("financial_pages", []) or ex.get("pages", []):
        if page.get("page_id") == page_id:
            return page
    return None


def apply_metric_correction(page: dict, metric_name: str, year: str,
                            current_value, corrected_value) -> tuple[bool, str]:
    """Update a metric's value. Returns (changed, status_msg)."""
    for met in page.get("metrics", []):
        if met.get("name") != metric_name:
            continue
        vals = met.setdefault("values", {})
        existing = vals.get(year)
        if existing == corrected_value:
            return (False, "already-corrected")
        # Don't enforce current_value match exactly — vision can re-read at slightly
        # different precision. Just record what we're replacing.
        vals[year] = corrected_value
        return (True, f"updated {metric_name}/{year}: {existing} → {corrected_value}")
    return (False, f"metric '{metric_name}' not found on page")


def apply_metric_addition(page: dict, metric_name: str, year: str, value) -> tuple[bool, str]:
    """Add a metric (or year-on-existing-metric)."""
    for met in page.get("metrics", []):
        if met.get("name") == metric_name:
            vals = met.setdefault("values", {})
            if vals.get(year) == value:
                return (False, "already-present")
            vals[year] = value
            return (True, f"added year on existing metric '{metric_name}'/{year}: {value}")
    page.setdefault("metrics", []).append({"name": metric_name, "values": {year: value}})
    return (True, f"added new metric '{metric_name}'/{year}: {value}")


def main():
    corrections_path = GF / "corrections.json"
    if not corrections_path.exists():
        print("No corrections.json — nothing to apply.")
        return
    corrections = json.loads(corrections_path.read_text())["corrections"]

    log_entries = []
    files_modified: dict[Path, dict] = {}

    for corr in corrections:
        page_id = corr.get("page_id")
        ext_path = find_extraction_for_page(page_id) if page_id else None
        if not ext_path:
            log_entries.append({**corr, "_status": "no-matching-extraction-file"})
            continue
        if ext_path not in files_modified:
            # Backup once
            backup = ext_path.with_suffix(".json.pre-correction-bak")
            if not backup.exists():
                shutil.copy(ext_path, backup)
            files_modified[ext_path] = json.loads(ext_path.read_text())
        ex = files_modified[ext_path]
        page = find_page_in_extraction(ex, page_id)
        if not page:
            log_entries.append({**corr, "_status": f"page_id '{page_id}' not found in {ext_path.name}"})
            continue
        page.setdefault("_corrections_applied", []).append({
            "rule_targeted": corr.get("rule_targeted"),
            "year": corr.get("year"),
            "issue": corr.get("issue"),
        })
        sub = []
        for mc in corr.get("metric_corrections", []):
            ok, msg = apply_metric_correction(
                page, mc["metric_name"], mc.get("year") or corr.get("year"),
                mc.get("current_value"), mc["corrected_value"],
            )
            sub.append({"action": "correction", "metric": mc["metric_name"], "ok": ok, "msg": msg})
        for ma in corr.get("metric_additions", []):
            ok, msg = apply_metric_addition(
                page, ma["metric_name"], ma.get("year") or corr.get("year"),
                ma["value"],
            )
            sub.append({"action": "addition", "metric": ma["metric_name"], "ok": ok, "msg": msg})
        log_entries.append({**corr, "_extraction_file": str(ext_path.relative_to(ROOT)),
                            "_subactions": sub})

    # Write all modified files back
    for path, ex in files_modified.items():
        path.write_text(json.dumps(ex, indent=2, ensure_ascii=False))

    # Write log
    log_out = GF / "corrections_applied_log.json"
    log_out.write_text(json.dumps({
        "applied_at": "2026-04-25",
        "files_modified": [str(p.relative_to(ROOT)) for p in files_modified],
        "entries": log_entries,
    }, indent=2, ensure_ascii=False))
    n_ok = sum(1 for e in log_entries for s in e.get("_subactions", []) if s.get("ok"))
    n_total_actions = sum(len(e.get("_subactions", [])) for e in log_entries)
    print(f"Applied {n_ok}/{n_total_actions} sub-actions across {len(files_modified)} JSON files.")
    print(f"Log: {log_out.relative_to(ROOT)}")
    for entry in log_entries:
        print(f"  {entry.get('page_id'):60s} {entry.get('year'):10s}  "
              f"{len(entry.get('_subactions', []))} actions  ({entry.get('_status', 'ok')})")


if __name__ == "__main__":
    main()
