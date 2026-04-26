#!/usr/bin/env python3.12
"""Auto-discovering merged-graph builder.

Combines the curated 10 companies (TSMC + 9 baseline) with every
{key}_extraction.json found under graphify-financial/<key>/.

Output: graphify-financial/graph-financial.json (replaces the old 10-company
version) — same schema as before, schema_version bumped to financial-v3.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"

# Load the existing curated COMPANIES dict for the original 10 (canonical metadata)
import sys; sys.path.insert(0, str(ROOT / "scripts"))
from build_merged_graph import (
    COMPANIES as CURATED_COMPANIES, CANONICAL_MAP, CANONICAL_UNITS,
    to_canonical, normalize_to_native_currency_native_unit, native_to_usd_value,
    FX_TO_USD, FX_SOURCES, FX_FETCHED_AT,
)
from year_normalizer import normalize as normalize_year


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower().strip()).strip("_")


def discover_companies() -> dict[str, dict]:
    """Return {key: meta} for every company with a usable extraction.

    For curated keys, use CURATED_COMPANIES. For others, derive metadata
    from the extraction JSON's top-level fields.
    """
    out = dict(CURATED_COMPANIES)
    for d in sorted(GF.iterdir()):
        if not d.is_dir():
            continue
        ext = d / f"{d.name}_extraction.json"
        if not ext.exists():
            continue
        if d.name in out:
            continue  # curated already
        try:
            j = json.loads(ext.read_text())
        except Exception:
            continue
        out[d.name] = {
            "label": j.get("company") or d.name,
            "country": j.get("country") or "Unknown",
            "industry": j.get("industry") or "unknown",
            "ticker": j.get("ticker"),
        }
    return out


def load_extraction(key: str) -> dict:
    if key == "tsmc":
        fin = json.loads((GF / "tsmc/tsmc_financials.json").read_text())
        ppl = json.loads((GF / "tsmc/tsmc_people.json").read_text())
        return {
            "company": "TSMC", "ticker": "TWSE:2330,NYSE:TSM",
            "currency_default": "TWD", "fiscal_year_end": "December",
            "financial_pages": fin["pages"], "people_pages": ppl["pages"],
        }
    return json.loads((GF / key / f"{key}_extraction.json").read_text())


def collect_canonical_metrics(extraction: dict) -> dict:
    PRIORITY = {"income_statement": 4, "balance_sheet": 4, "5_year_highlights": 3,
                "financial_highlights": 2, "segment_breakdown": 1,
                "revenue_breakdown": 1, "cash_flow": 2, "capital_structure": 1,
                "other": 0, "non_financial": -1}
    out = {}
    for page in extraction.get("financial_pages", []):
        if not page.get("is_financial_table") or not page.get("is_company_actual", True):
            continue
        prio = PRIORITY.get(page.get("table_type", "other"), 0)
        currency = page.get("currency") or extraction.get("currency_default") or "USD"
        unit = page.get("unit") or "as_is"
        for met in page.get("metrics", []):
            canon = to_canonical(met["name"])
            if not canon:
                continue
            for y_label, v in (met.get("values") or {}).items():
                if not isinstance(v, (int, float)):
                    continue
                y, period, is_forecast = normalize_year(y_label)
                if y is None:
                    continue
                # Skip forecasts in canonical (FY-actual is preferred for cross-company comparison);
                # quarterly periods also excluded from the cross-company canonical table since they
                # would compete with full-year values
                if is_forecast or (period and period != "FY" and period != "FY3" and period != "as_of"):
                    continue
                key = (canon, y)
                v_native = normalize_to_native_currency_native_unit(v, unit, currency)
                if canon in ("gross_margin_pct", "operating_margin_pct"):
                    v_native = v
                v_usd = native_to_usd_value(v_native, currency) if canon not in (
                    "gross_margin_pct", "operating_margin_pct", "employees"
                ) else v_native
                existing = out.get(key)
                if existing and existing["_prio"] >= prio:
                    continue
                out[key] = {
                    "_prio": prio,
                    "value_native": v_native, "value_usd": v_usd,
                    "currency": currency, "source_page": page["page_id"],
                }
    final = {}
    for (canon, year), v in out.items():
        final.setdefault(canon, {"unit": CANONICAL_UNITS.get(canon, "unknown"), "values": {}})
        final[canon]["values"][year] = {
            "native": v["value_native"], "usd": v["value_usd"],
            "currency": v["currency"], "source_page": v["source_page"],
        }
    return final


def main():
    companies = discover_companies()
    nodes, edges = [], []
    person_dedup: dict[str, str] = {}
    n_skipped = 0

    for key, meta in companies.items():
        # For curated TSMC, don't try .extraction.json
        ext_path = GF / key / f"{key}_extraction.json"
        if key != "tsmc" and not ext_path.exists():
            n_skipped += 1
            continue
        try:
            ex = load_extraction(key)
        except Exception as e:
            print(f"  [skip] {key}: failed to load — {e}")
            n_skipped += 1
            continue

        canonical = collect_canonical_metrics(ex)
        native_metrics: dict = {}
        for page in ex.get("financial_pages", []):
            if not page.get("is_financial_table"):
                continue
            for m in page.get("metrics", []):
                native_metrics.setdefault(m["name"], {
                    "page": page["page_id"],
                    "currency": page.get("currency"),
                    "unit": page.get("unit"),
                    "values": {},
                })
                for y, v in (m.get("values") or {}).items():
                    if isinstance(v, (int, float)):
                        native_metrics[m["name"]]["values"][y] = v

        nodes.append({
            "id": f"company_{key}",
            "label": meta.get("label", key),
            "norm_label": key,
            "type": "company", "file_type": "company",
            "country": meta.get("country"),
            "industry": meta.get("industry"),
            "ticker": meta.get("ticker"),
            "currency_default": ex.get("currency_default"),
            "fiscal_year_end": ex.get("fiscal_year_end"),
            "metrics_canonical": canonical,
            "metrics_native": native_metrics,
            "community": 0,
            "confidence_score": 1.0,
            "source": "EXTRACTED",
            "extraction_type": "EXTRACTED",
        })

        for ppage in ex.get("people_pages", []):
            for person in ppage.get("people", []):
                pname = (person.get("name") or "").strip()
                if not pname:
                    continue
                nkey = norm_name(pname)
                if nkey in person_dedup:
                    pid = person_dedup[nkey]
                    existing = next(n for n in nodes if n["id"] == pid)
                    existing.setdefault("linked_companies", [])
                    if key not in existing["linked_companies"]:
                        existing["linked_companies"].append(key)
                else:
                    pid = f"person_{nkey}"
                    person_dedup[nkey] = pid
                    nodes.append({
                        "id": pid, "label": pname, "norm_label": nkey,
                        "type": "person", "file_type": "person",
                        "person_type": person.get("type", "other"),
                        "primary_role": person.get("role", ""),
                        "primary_company": key,
                        "linked_companies": [key],
                        "tenure_start": person.get("tenure_start"),
                        "education": person.get("education"),
                        "concurrent_roles": person.get("concurrent_roles", []),
                        "community": 0,
                        "confidence_score": 0.95,
                        "source": "EXTRACTED",
                        "extraction_type": "EXTRACTED",
                    })
                rel = {
                    "board_director": "serves_on_board_of",
                    "independent_director": "serves_on_board_of",
                    "executive_officer": "executive_of",
                    "senior_vp": "executive_of",
                    "vp": "executive_of",
                    "committee_member": "serves_on_committee_of",
                    "other": "affiliated_with",
                }.get(person.get("type", "other"), "affiliated_with")
                edges.append({
                    "source": pid, "target": f"company_{key}",
                    "relation": rel, "role": person.get("role", ""),
                    "confidence": 0.95, "confidence_score": 0.95,
                    "source_file": "vision_extraction",
                    "weight": 2.0 if "director" in person.get("type", "") else 1.0,
                })

    graph = {
        "directed": True, "multigraph": False,
        "graph": {
            "title": f"Multi-Company Financial Subgraph ({sum(1 for n in nodes if n['type']=='company')} companies)",
            "generated_at": "2026-04-25",
            "extractor": "sonnet-4.6 vision + pdftoppm",
            "schema_version": "financial-v3",
            "fx_to_usd": FX_TO_USD, "fx_sources": FX_SOURCES,
            "fx_fetched_at": FX_FETCHED_AT,
            "canonical_metric_keys": list(CANONICAL_UNITS.keys()),
            "canonical_metric_units": CANONICAL_UNITS,
        },
        "nodes": nodes, "links": edges, "hyperedges": [],
    }

    out = GF / "graph-financial.json"
    out.write_text(json.dumps(graph, indent=2, ensure_ascii=False))

    n_companies = sum(1 for n in nodes if n["type"] == "company")
    n_people = sum(1 for n in nodes if n["type"] == "person")
    print(f"Wrote {out}")
    print(f"  Companies: {n_companies}")
    print(f"  People:    {n_people} unique (deduped across companies)")
    print(f"  Edges:     {len(edges)}")
    print(f"  Skipped:   {n_skipped}")
    multi = [n for n in nodes if n["type"] == "person" and len(n.get("linked_companies", [])) > 1]
    print(f"  People appearing on >1 company: {len(multi)}")
    for p in multi[:10]:
        print(f"    {p['label']}: {p['linked_companies']}")


if __name__ == "__main__":
    main()
