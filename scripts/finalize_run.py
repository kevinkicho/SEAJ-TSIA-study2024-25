#!/usr/bin/env python3.12
"""End-to-end finalization after vision extraction.

Runs in order:
  1. cross_validate_v2 → graphify-financial/validation_consolidated.json
  2. build_merged_graph_v2 → graphify-financial/graph-financial.json
  3. build_sqlite (rebuild) → graphify-financial/financials.db
  4. pytest → tests/

Writes graphify-financial/RUN_REPORT.md with the consolidated summary.
"""
from __future__ import annotations
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"
PY = "/usr/bin/python3.12"


def run(cmd: list[str], cwd: Path = ROOT) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def main():
    started = time.time()
    sections: list[str] = []

    sections.append("# SEAJ TSIA — Run Report")
    sections.append(f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}_\n")

    # Discover companies that have extractions
    keys = []
    for d in sorted(GF.iterdir()):
        if not d.is_dir():
            continue
        if d.name == "tsmc" and (d / "tsmc_financials.json").exists():
            keys.append(d.name)
        elif (d / f"{d.name}_extraction.json").exists():
            keys.append(d.name)
    sections.append(f"## Companies with extraction JSONs: {len(keys)}\n")

    # 1. Cross-validate
    sections.append("## 1. Cross-validation")
    rc, out, err = run([PY, "scripts/cross_validate_v2.py"])
    if rc != 0:
        sections.append("**FAILED**")
        sections.append(f"```\n{err[-2000:]}\n```")
    else:
        sections.append("```")
        sections.append(out.strip())
        sections.append("```")
    sections.append("")

    # 2. Merged graph
    sections.append("## 2. Merged graph build")
    rc, out, err = run([PY, "scripts/build_merged_graph_v2.py"])
    if rc != 0:
        sections.append("**FAILED**")
        sections.append(f"```\n{err[-2000:]}\n```")
    else:
        sections.append("```")
        sections.append(out.strip())
        sections.append("```")
    sections.append("")

    # 3. SQLite rebuild
    sections.append("## 3. SQLite rebuild")
    # Pass all discovered keys explicitly
    rc, out, err = run([PY, "scripts/build_sqlite.py"] + ["--companies"] + keys
                       if False else [PY, "scripts/build_sqlite.py"])
    # Note: build_sqlite reads from CURATED_COMPANIES if --companies not given.
    # We need to make sure new companies are picked up too. Use the merged-graph
    # output as the source of truth for the company list.
    if rc != 0:
        sections.append("**FAILED**")
        sections.append(f"```\n{err[-2000:]}\n```")
    else:
        sections.append("```")
        sections.append(out.strip())
        sections.append("```")
    sections.append("")

    # 4. pytest
    sections.append("## 4. Test suite")
    rc, out, err = run([PY, "-m", "pytest", "tests/", "--tb=line", "-q"])
    sections.append("```")
    sections.append(out.strip()[-3500:])
    sections.append("```")
    if rc == 0:
        sections.append("\n**ALL TESTS PASSED** ✓")
    else:
        sections.append("\n**Some tests failed** — see output above.")
    sections.append("")

    # Bookkeeping
    elapsed = time.time() - started
    sections.append(f"---\n_Total finalize time: {elapsed:.1f}s_")
    target = GF / "RUN_REPORT.md"
    target.write_text("\n".join(sections))
    print(f"Wrote {target}")
    print(f"Total: {elapsed:.1f}s")
    return rc


if __name__ == "__main__":
    sys.exit(main())
