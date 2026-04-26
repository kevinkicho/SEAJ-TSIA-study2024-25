#!/usr/bin/env python3.12
"""Cross-validate every extraction file present under graphify-financial/<key>/.

Auto-discovers, runs the same battery of subtotal / cross-page rules used in
cross_validate.py, and writes graphify-financial/validation_consolidated.json.

Idempotent: overwrites the consolidated file each run.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"

# Reuse the exact rules from cross_validate.py
sys.path.insert(0, str(ROOT / "scripts"))
from cross_validate import (
    RULES, collect_metrics, cross_page_consistency,
)


def discover_keys() -> list[str]:
    keys = []
    for d in sorted(GF.iterdir()):
        if not d.is_dir():
            continue
        if d.name == "tsmc":
            if (d / "tsmc_financials.json").exists():
                keys.append("tsmc")
            continue
        if (d / f"{d.name}_extraction.json").exists():
            keys.append(d.name)
    return keys


def load(key: str) -> dict:
    if key == "tsmc":
        fin = json.loads((GF / "tsmc/tsmc_financials.json").read_text())
        ppl = json.loads((GF / "tsmc/tsmc_people.json").read_text())
        return {"financial_pages": fin["pages"], "people_pages": ppl["pages"]}
    return json.loads((GF / key / f"{key}_extraction.json").read_text())


def main():
    keys = discover_keys()
    out: dict[str, dict] = {}
    for key in keys:
        try:
            ex = load(key)
        except Exception as e:
            print(f"[skip] {key}: load failed — {e}")
            continue
        pages = collect_metrics(ex)
        # Run rules per page per year
        checks = []
        years_seen = set()
        for pid, m in pages:
            ys = sorted({y for vals in m.values() for y in vals})
            for y in ys:
                years_seen.add(y)
                for rule in RULES:
                    res = rule(m, y)
                    if res is None:
                        continue
                    rule_name, expected, computed = res
                    ok = abs(expected - computed) <= max(abs(expected) * 0.001, 1)
                    checks.append({
                        "page": pid, "year": y, "rule": rule_name,
                        "expected": expected, "computed": computed,
                        "pass": ok,
                    })
        cf = cross_page_consistency(pages)
        n_people = sum(len(p.get("people", [])) for p in ex.get("people_pages", []))
        passed = sum(1 for c in checks if c["pass"])
        out[key] = {
            "checks": checks,
            "cross_page_conflicts": cf,
            "passed": passed, "total": len(checks),
            "years": sorted(years_seen),
            "people": n_people,
        }
        print(f"  {key:30s}  checks {passed}/{len(checks):3d}, "
              f"cross_page_conflicts {len(cf):2d}, people {n_people}")

    target = GF / "validation_consolidated.json"
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nWrote {target}")
    n_pass = sum(c["passed"] for c in out.values())
    n_tot = sum(c["total"] for c in out.values())
    print(f"  Total checks: {n_tot}, passed {n_pass} "
          f"({100*n_pass/max(n_tot,1):.0f}%)")


if __name__ == "__main__":
    main()
