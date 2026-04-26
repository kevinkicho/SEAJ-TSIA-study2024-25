"""Schema integrity: foreign-key-like consistency, no orphan rows, expected tables."""
import pytest

REQUIRED_TABLES = {
    "companies", "financial_pages", "financial_metrics",
    "people", "person_affiliations",
    "extraction_runs", "validation_issues", "fx_rates",
}


def test_required_tables_exist(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    names = {r["name"] for r in rows}
    missing = REQUIRED_TABLES - names
    assert not missing, f"missing tables: {missing}"


def test_companies_have_unique_ids(conn):
    rows = conn.execute("""
        SELECT company_id, COUNT(*) c FROM companies GROUP BY company_id HAVING c > 1
    """).fetchall()
    assert not rows, f"duplicate company_id: {[r['company_id'] for r in rows]}"


def test_company_ids_nonempty(conn):
    rows = conn.execute("SELECT company_id FROM companies").fetchall()
    assert rows, "no companies in DB"
    for r in rows:
        assert r["company_id"] and r["company_id"].strip()


def test_no_orphan_pages(conn):
    rows = conn.execute("""
        SELECT fp.page_id, fp.company_id FROM financial_pages fp
        LEFT JOIN companies c USING(company_id)
        WHERE c.company_id IS NULL
    """).fetchall()
    assert not rows, f"orphan pages reference unknown company: {[(r['page_id'],r['company_id']) for r in rows]}"


def test_no_orphan_metrics(conn):
    rows = conn.execute("""
        SELECT fm.id, fm.page_id FROM financial_metrics fm
        LEFT JOIN financial_pages fp USING(page_id)
        WHERE fp.page_id IS NULL
    """).fetchall()
    assert not rows, f"orphan metrics reference unknown page: {len(rows)} rows"


def test_no_orphan_affiliations_company(conn):
    rows = conn.execute("""
        SELECT pa.id FROM person_affiliations pa
        LEFT JOIN companies c USING(company_id)
        WHERE c.company_id IS NULL
    """).fetchall()
    assert not rows, f"affiliations reference unknown company: {len(rows)}"


def test_no_orphan_affiliations_person(conn):
    rows = conn.execute("""
        SELECT pa.id FROM person_affiliations pa
        LEFT JOIN people p USING(person_id)
        WHERE p.person_id IS NULL
    """).fetchall()
    assert not rows, f"affiliations reference unknown person: {len(rows)}"


def test_indexes_exist(conn):
    expected = {
        "idx_metrics_company_year", "idx_metrics_canonical",
        "idx_pages_company", "idx_aff_person", "idx_aff_company",
    }
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()
    names = {r["name"] for r in rows}
    missing = expected - names
    assert not missing, f"missing indexes: {missing}"


def test_every_company_has_at_least_one_page(conn):
    rows = conn.execute("""
        SELECT c.company_id FROM companies c
        LEFT JOIN financial_pages fp USING(company_id)
        GROUP BY c.company_id
        HAVING COUNT(fp.page_id) = 0
    """).fetchall()
    assert not rows, f"companies with zero pages: {[r['company_id'] for r in rows]}"


def test_extraction_runs_recorded(conn):
    n = conn.execute("SELECT COUNT(*) n FROM extraction_runs").fetchone()["n"]
    n_co = conn.execute("SELECT COUNT(*) n FROM companies").fetchone()["n"]
    assert n == n_co, f"extraction_runs ({n}) should match companies ({n_co})"
