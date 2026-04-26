#!/usr/bin/env python3.12
"""Build financials.db — structured SQLite store for the financial graph.

Reads existing per-company extraction JSONs, FX rates, and validation
results, then writes a single queryable database alongside the JSON files.

Usage:
    python3.12 scripts/build_sqlite.py            # build / rebuild from scratch
    python3.12 scripts/build_sqlite.py --append   # add new companies without dropping existing rows

Schema (see README at bottom of this file for query examples):
    companies, financial_pages, financial_metrics,
    people, person_affiliations,
    extraction_runs, validation_issues, fx_rates
"""
from __future__ import annotations
import argparse, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"
DB_PATH = GF / "financials.db"

# Reuse canonical-metric mapping from build_merged_graph
sys.path.insert(0, str(ROOT / "scripts"))
from build_merged_graph import (
    COMPANIES, CANONICAL_MAP, CANONICAL_UNITS,
    to_canonical, normalize_to_native_currency_native_unit, native_to_usd_value,
    FX_TO_USD, FX_SOURCES, FX_FETCHED_AT,
)
from year_normalizer import normalize as normalize_year


SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    company_id        TEXT PRIMARY KEY,
    label             TEXT NOT NULL,
    country           TEXT,
    industry          TEXT,
    ticker            TEXT,
    currency_default  TEXT,
    fiscal_year_end   TEXT,
    source_pdf        TEXT,
    extracted_by      TEXT,
    extracted_at      TEXT
);

CREATE TABLE IF NOT EXISTS financial_pages (
    page_id            TEXT PRIMARY KEY,
    company_id         TEXT NOT NULL,
    page_num           INTEGER,
    is_financial_table INTEGER,
    is_company_actual  INTEGER,
    table_type         TEXT,
    currency           TEXT,
    unit               TEXT,
    fiscal_year_end    TEXT,
    notes              TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS financial_metrics (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id            TEXT NOT NULL,
    company_id         TEXT NOT NULL,
    metric_name        TEXT NOT NULL,
    canonical_name     TEXT,
    year               TEXT NOT NULL,
    period             TEXT,                  -- FY, FY3, Q1-Q4, H1, H2, 9M, as_of
    is_forecast        INTEGER DEFAULT 0,
    raw_year_label     TEXT,                  -- the original printed label, e.g., "FY2024_3Q"
    value_native       REAL,
    value_native_whole REAL,
    value_usd          REAL,
    currency           TEXT,
    unit               TEXT,
    FOREIGN KEY (page_id)    REFERENCES financial_pages(page_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS people (
    person_id        TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    norm_name        TEXT NOT NULL,
    primary_company  TEXT,
    primary_role     TEXT,
    person_type      TEXT,
    tenure_start     TEXT,
    education        TEXT
);

CREATE TABLE IF NOT EXISTS person_affiliations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id         TEXT NOT NULL,
    company_id        TEXT NOT NULL,
    role              TEXT,
    affiliation_type  TEXT,
    source_page       TEXT,
    confidence        REAL,
    notes             TEXT,
    concurrent_roles  TEXT,
    FOREIGN KEY (person_id)  REFERENCES people(person_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS extraction_runs (
    run_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id          TEXT NOT NULL,
    source_pdf          TEXT,
    extracted_at        TEXT,
    extracted_by        TEXT,
    n_pages_rasterized  INTEGER,
    n_metrics_extracted INTEGER,
    n_people_extracted  INTEGER,
    validation_passed   INTEGER,
    validation_total    INTEGER,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS validation_issues (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id  TEXT NOT NULL,
    page_id     TEXT,
    year        TEXT,
    rule        TEXT,
    expected    REAL,
    computed    REAL,
    severity    TEXT,
    pass_       INTEGER,
    detail      TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS fx_rates (
    currency     TEXT PRIMARY KEY,
    rate_to_usd  REAL NOT NULL,
    source       TEXT,
    fetched_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_metrics_company_year ON financial_metrics (company_id, year);
CREATE INDEX IF NOT EXISTS idx_metrics_canonical    ON financial_metrics (canonical_name);
CREATE INDEX IF NOT EXISTS idx_metrics_company_can  ON financial_metrics (company_id, canonical_name, year);
CREATE INDEX IF NOT EXISTS idx_pages_company        ON financial_pages    (company_id);
CREATE INDEX IF NOT EXISTS idx_aff_person           ON person_affiliations (person_id);
CREATE INDEX IF NOT EXISTS idx_aff_company          ON person_affiliations (company_id);
CREATE INDEX IF NOT EXISTS idx_validation_company   ON validation_issues  (company_id);
"""

PDF_BY_KEY = {
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


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower().strip()).strip("_")


def page_num_from_id(page_id: str) -> int | None:
    m = re.search(r"_p(\d+)", page_id)
    return int(m.group(1)) if m else None


def load_extraction(key: str) -> dict:
    """Return unified shape: financial_pages[], people_pages[], company, currency_default, ..."""
    if key == "tsmc":
        fin = json.loads((GF / "tsmc/tsmc_financials.json").read_text())
        ppl = json.loads((GF / "tsmc/tsmc_people.json").read_text())
        return {
            "company": "TSMC",
            "ticker": "TWSE:2330,NYSE:TSM",
            "currency_default": "TWD",
            "fiscal_year_end": "December",
            "extracted_by": fin.get("extracted_by"),
            "extracted_at": fin.get("extracted_at"),
            "source_pdf": fin.get("source_pdf"),
            "financial_pages": fin["pages"],
            "people_pages": ppl["pages"],
        }
    return json.loads((GF / key / f"{key}_extraction.json").read_text())


def insert_company(conn: sqlite3.Connection, key: str, ex: dict) -> None:
    meta = get_company_meta(key, ex)
    conn.execute(
        """INSERT OR REPLACE INTO companies
           (company_id, label, country, industry, ticker, currency_default,
            fiscal_year_end, source_pdf, extracted_by, extracted_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            key,
            meta.get("label", ex.get("company", key)),
            meta.get("country"),
            meta.get("industry"),
            meta.get("ticker") or ex.get("ticker"),
            ex.get("currency_default"),
            ex.get("fiscal_year_end"),
            ex.get("source_pdf") or PDF_BY_KEY.get(key),
            ex.get("extracted_by"),
            ex.get("extracted_at"),
        ),
    )


def insert_pages_and_metrics(conn: sqlite3.Connection, key: str, ex: dict) -> tuple[int, int]:
    """Returns (n_pages, n_metric_rows)."""
    n_pages = 0
    n_metric_rows = 0
    default_currency = ex.get("currency_default")
    for page in ex.get("financial_pages", []):
        page_id = page["page_id"]
        currency = page.get("currency") or default_currency
        unit = page.get("unit")
        conn.execute(
            """INSERT OR REPLACE INTO financial_pages
               (page_id, company_id, page_num, is_financial_table, is_company_actual,
                table_type, currency, unit, fiscal_year_end, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                page_id, key, page_num_from_id(page_id),
                1 if page.get("is_financial_table") else 0,
                1 if page.get("is_company_actual") else 0,
                page.get("table_type"),
                currency, unit,
                page.get("fiscal_year_end") or ex.get("fiscal_year_end"),
                page.get("notes"),
            ),
        )
        n_pages += 1
        if not page.get("is_financial_table"):
            continue
        for met in page.get("metrics", []):
            metric_name = met["name"]
            canonical = to_canonical(metric_name)
            for y_label, v in (met.get("values") or {}).items():
                if not isinstance(v, (int, float)):
                    continue
                year, period, is_forecast = normalize_year(y_label)
                if year is None:
                    continue  # truly unparseable label
                whole = normalize_to_native_currency_native_unit(v, unit, currency)
                if canonical in ("gross_margin_pct", "operating_margin_pct"):
                    whole = v
                    usd = v
                elif canonical == "employees":
                    usd = whole
                else:
                    usd = native_to_usd_value(whole, currency) if currency else None
                conn.execute(
                    """INSERT INTO financial_metrics
                       (page_id, company_id, metric_name, canonical_name, year,
                        period, is_forecast, raw_year_label,
                        value_native, value_native_whole, value_usd, currency, unit)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (page_id, key, metric_name, canonical, year,
                     period, 1 if is_forecast else 0, y_label,
                     v, whole, usd, currency, unit),
                )
                n_metric_rows += 1
    return n_pages, n_metric_rows


def insert_people(conn: sqlite3.Connection, key: str, ex: dict) -> int:
    n = 0
    for ppage in ex.get("people_pages", []):
        page_id = ppage.get("page_id")
        for person in ppage.get("people", []):
            name = (person.get("name") or "").strip()
            if not name:
                continue
            nname = norm_name(name)
            person_id = f"person_{nname}"
            existing = conn.execute(
                "SELECT person_id FROM people WHERE person_id=?", (person_id,)
            ).fetchone()
            if not existing:
                conn.execute(
                    """INSERT INTO people (person_id, name, norm_name, primary_company,
                                           primary_role, person_type, tenure_start, education)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (person_id, name, nname, key,
                     person.get("role"), person.get("type"),
                     person.get("tenure_start"), person.get("education")),
                )
            rel = {
                "board_director":     "serves_on_board_of",
                "independent_director": "serves_on_board_of",
                "executive_officer":  "executive_of",
                "senior_vp":          "executive_of",
                "vp":                 "executive_of",
                "committee_member":   "serves_on_committee_of",
            }.get(person.get("type", ""), "affiliated_with")
            concurrent = json.dumps(person.get("concurrent_roles", []), ensure_ascii=False)
            conn.execute(
                """INSERT INTO person_affiliations
                   (person_id, company_id, role, affiliation_type, source_page, confidence,
                    notes, concurrent_roles)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (person_id, key, person.get("role"), rel, page_id, 0.95,
                 person.get("notes"), concurrent),
            )
            n += 1
    return n


def insert_extraction_run(conn, key, ex, n_pages, n_metrics, n_people, val_passed, val_total):
    conn.execute(
        """INSERT INTO extraction_runs
           (company_id, source_pdf, extracted_at, extracted_by,
            n_pages_rasterized, n_metrics_extracted, n_people_extracted,
            validation_passed, validation_total)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (key, ex.get("source_pdf") or PDF_BY_KEY.get(key),
         ex.get("extracted_at"), ex.get("extracted_by"),
         n_pages, n_metrics, n_people, val_passed, val_total),
    )


def insert_validation(conn, val_data: dict) -> None:
    for company_id, info in val_data.items():
        for chk in info.get("checks", []):
            conn.execute(
                """INSERT INTO validation_issues
                   (company_id, page_id, year, rule, expected, computed, severity, pass_, detail)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (company_id, chk.get("page"), chk.get("year"), chk.get("rule"),
                 chk.get("expected"), chk.get("computed"),
                 "info" if chk.get("pass") else "warning",
                 1 if chk.get("pass") else 0, None),
            )
        for cf in info.get("cross_page_conflicts", []):
            conn.execute(
                """INSERT INTO validation_issues
                   (company_id, page_id, year, rule, expected, computed, severity, pass_, detail)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (company_id, cf.get("page"), cf.get("year"),
                 f"cross_page:{cf.get('metric','')}",
                 cf.get("expected"), cf.get("computed"),
                 "warning", 0, json.dumps(cf, ensure_ascii=False)),
            )


def insert_fx(conn) -> None:
    for cur, rate in FX_TO_USD.items():
        conn.execute(
            "INSERT OR REPLACE INTO fx_rates (currency, rate_to_usd, source, fetched_at) VALUES (?,?,?,?)",
            (cur, rate, FX_SOURCES.get(cur, ""), FX_FETCHED_AT),
        )


def discover_keys() -> list[str]:
    """Auto-discover every company key with an extraction file under graphify-financial/<key>/."""
    keys = []
    for d in sorted(GF.iterdir()):
        if not d.is_dir():
            continue
        if d.name == "tsmc" and (d / "tsmc_financials.json").exists():
            keys.append("tsmc")
            continue
        if (d / f"{d.name}_extraction.json").exists():
            keys.append(d.name)
    return keys


def get_company_meta(key: str, ex: dict) -> dict:
    """Curated metadata wins; fall back to extraction's top-level fields."""
    if key in COMPANIES:
        m = dict(COMPANIES[key])
        # Backfill missing fields from extraction
        if not m.get("country") and ex.get("country"):
            m["country"] = ex["country"]
        if not m.get("industry") and ex.get("industry"):
            m["industry"] = ex["industry"]
        return m
    return {
        "label": ex.get("company") or key,
        "country": ex.get("country") or "Unknown",
        "industry": ex.get("industry") or "unknown",
        "ticker": ex.get("ticker"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--append", action="store_true",
                    help="don't drop existing rows; just upsert")
    ap.add_argument("--companies", nargs="*", default=None,
                    help="only ingest these company keys (default: auto-discover all extractions on disk)")
    args = ap.parse_args()

    if not args.append and DB_PATH.exists():
        DB_PATH.unlink()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    keys = args.companies or discover_keys()
    total_pages = total_metrics = total_people = 0

    val_path = GF / "validation_consolidated.json"
    val_data = json.loads(val_path.read_text()) if val_path.exists() else {}

    for key in keys:
        ext_path = GF / key / f"{key}_extraction.json"
        if key != "tsmc" and not ext_path.exists():
            print(f"  [skip] {key}: no extraction file", file=sys.stderr)
            continue
        ex = load_extraction(key)
        insert_company(conn, key, ex)
        n_pages, n_metrics = insert_pages_and_metrics(conn, key, ex)
        n_people = insert_people(conn, key, ex)
        v = val_data.get(key, {})
        insert_extraction_run(conn, key, ex, n_pages, n_metrics, n_people,
                              v.get("passed", 0), v.get("total", 0))
        total_pages += n_pages; total_metrics += n_metrics; total_people += n_people
        print(f"  {key}: {n_pages} pages, {n_metrics} metric-rows, {n_people} people-affs"
              + (f", validation {v.get('passed',0)}/{v.get('total',0)}" if v else ""))

    insert_validation(conn, val_data)
    insert_fx(conn)
    conn.commit()

    n_companies = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    n_unique_people = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
    n_affiliations = conn.execute("SELECT COUNT(*) FROM person_affiliations").fetchone()[0]
    n_val_issues = conn.execute("SELECT COUNT(*) FROM validation_issues WHERE pass_=0").fetchone()[0]
    n_canonical = conn.execute(
        "SELECT COUNT(DISTINCT canonical_name) FROM financial_metrics WHERE canonical_name IS NOT NULL"
    ).fetchone()[0]

    print(f"\n=== {DB_PATH.name} ===")
    print(f"  companies         : {n_companies}")
    print(f"  financial_pages   : {total_pages}")
    print(f"  financial_metrics : {total_metrics} ({n_canonical} canonical metrics)")
    print(f"  people (unique)   : {n_unique_people}")
    print(f"  person_affiliations: {n_affiliations}")
    print(f"  validation issues : {n_val_issues} (failed checks)")
    print(f"  size              : {DB_PATH.stat().st_size:,} bytes")

    # Sample queries to demonstrate the DB works
    print("\n=== Sample query: revenue by company-year (USD millions) ===")
    rows = conn.execute("""
        SELECT c.label, fm.year, ROUND(fm.value_usd / 1e6, 1) AS rev_usd_m, fm.currency
        FROM financial_metrics fm
        JOIN companies c ON c.company_id = fm.company_id
        WHERE fm.canonical_name = 'revenue'
        ORDER BY fm.year DESC, fm.value_usd DESC
        LIMIT 15
    """).fetchall()
    for r in rows:
        print(f"  {r[0]:30s} {r[1]} {r[2]:>12,} M USD  ({r[3]})")

    print("\n=== Sample query: cross-board people ===")
    rows = conn.execute("""
        SELECT p.name, COUNT(DISTINCT pa.company_id) n_companies,
               GROUP_CONCAT(DISTINCT pa.company_id) as companies
        FROM people p
        JOIN person_affiliations pa ON pa.person_id = p.person_id
        GROUP BY p.person_id
        HAVING n_companies > 1
        ORDER BY n_companies DESC
    """).fetchall()
    if rows:
        for r in rows:
            print(f"  {r[0]:25s}  ({r[1]} companies: {r[2]})")
    else:
        print("  (none yet — will surface more when full corpus is ingested)")

    conn.close()


if __name__ == "__main__":
    main()


# === Query examples (run with: sqlite3 graphify-financial/financials.db < query.sql) ===
#
# Revenue trend per company (canonical, USD-normalized):
#   SELECT c.label, fm.year, fm.value_usd
#   FROM financial_metrics fm JOIN companies c USING(company_id)
#   WHERE fm.canonical_name = 'revenue'
#   ORDER BY c.label, fm.year;
#
# All metrics for one company:
#   SELECT page_id, table_type, canonical_name, metric_name, year,
#          value_native, currency, unit
#   FROM financial_metrics fm JOIN financial_pages fp USING(page_id)
#   WHERE fm.company_id = 'tsmc'
#   ORDER BY year DESC, canonical_name;
#
# Cross-board / cross-exec people:
#   SELECT p.name, GROUP_CONCAT(pa.company_id) AS companies, GROUP_CONCAT(pa.role)
#   FROM people p JOIN person_affiliations pa USING(person_id)
#   GROUP BY p.person_id
#   HAVING COUNT(DISTINCT pa.company_id) > 1;
#
# Validation health by company:
#   SELECT er.company_id,
#          ROUND(100.0*er.validation_passed/NULLIF(er.validation_total,0), 1) AS pass_pct,
#          er.validation_passed, er.validation_total
#   FROM extraction_runs er
#   ORDER BY pass_pct;
