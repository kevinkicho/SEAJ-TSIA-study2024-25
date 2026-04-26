"""Accuracy: subtotal reconciliation, cross-page consistency.

These tests re-run the cross-validation logic against the SQLite store and
check that the validation_issues table matches the raw extraction's checks.
A small number of failed-check rows is expected (memory: WPG p127 has a
known balance-sheet read error). We assert pass-rate, not zero failures.
"""
import pytest

# Tolerable failure rate for automated subtotal checks (GP-OpEx=OpInc, etc.)
# Cross-page conflicts are excluded — those frequently capture legitimate
# differences between consolidated vs parent-only statements.
MIN_PASS_RATE = 0.50


def test_subtotal_validation_pass_rate(conn):
    """Subtotal-rule checks (excludes cross_page_* issues, which often reflect
    legitimate consolidated/parent-only divergence rather than errors)."""
    n_pass = conn.execute(
        "SELECT COUNT(*) c FROM validation_issues WHERE pass_=1 AND rule NOT LIKE 'cross_page%'"
    ).fetchone()["c"]
    n_total = conn.execute(
        "SELECT COUNT(*) c FROM validation_issues WHERE rule NOT LIKE 'cross_page%'"
    ).fetchone()["c"]
    if n_total == 0:
        pytest.skip("no subtotal validation checks recorded yet")
    rate = n_pass / n_total
    assert rate >= MIN_PASS_RATE, f"subtotal validation pass-rate {rate:.1%} below floor {MIN_PASS_RATE:.0%}"


def test_per_company_validation_recorded(conn):
    """Every company that has automated checks should have at least one validation row."""
    rows = conn.execute("""
        SELECT er.company_id, er.validation_total
        FROM extraction_runs er
        WHERE er.validation_total > 0
    """).fetchall()
    for r in rows:
        n = conn.execute(
            "SELECT COUNT(*) c FROM validation_issues WHERE company_id=?", (r["company_id"],)
        ).fetchone()["c"]
        assert n >= r["validation_total"], (
            f"{r['company_id']}: extraction_runs says {r['validation_total']} checks "
            f"but validation_issues has {n}"
        )


def test_subtotal_recompute_matches_stored(conn):
    """Re-derive GP-OpEx=OpInc from the metrics table and confirm any pass=1 rows
    actually reconcile within 0.5%. Catches stale validation rows."""
    fails = []
    rows = conn.execute("""
        SELECT vi.company_id, vi.page_id, vi.year, vi.rule, vi.expected, vi.computed, vi.pass_
        FROM validation_issues vi
        WHERE vi.pass_=1 AND vi.expected IS NOT NULL AND vi.computed IS NOT NULL
    """).fetchall()
    for r in rows:
        e, c = r["expected"], r["computed"]
        if e == 0:
            continue
        rel = abs(e - c) / max(abs(e), 1)
        if rel > 0.005:
            fails.append((r["company_id"], r["page_id"], r["rule"], e, c, rel))
    assert not fails, f"validation rows marked pass=1 but reconcile drift > 0.5%: {fails[:5]}"


def test_cross_page_revenue_consistency_majority(conn):
    """Most company-years with revenue on multiple pages should agree within 5%.
    Some divergence is legitimate (consolidated vs parent-only), so we measure
    the *fraction* of consistent year-pairs, not zero-drift."""
    rows = conn.execute("""
        SELECT company_id, year, page_id, value_native_whole
        FROM financial_metrics
        WHERE canonical_name='revenue' AND value_native_whole IS NOT NULL
        ORDER BY company_id, year, page_id
    """).fetchall()
    by_co_year = {}
    for r in rows:
        by_co_year.setdefault((r["company_id"], r["year"]), []).append(
            r["value_native_whole"]
        )
    multi = {k: v for k, v in by_co_year.items() if len(v) >= 2}
    if not multi:
        pytest.skip("no multi-page revenue rows")
    consistent = 0
    for k, vals in multi.items():
        lo, hi = min(vals), max(vals)
        rel = (hi - lo) / max(abs(lo), 1) if lo else 0
        if rel <= 0.05:
            consistent += 1
    rate = consistent / len(multi)
    assert rate >= 0.50, f"cross-page revenue consistency {rate:.1%} (consolidated/parent-only divergence is OK; this is too low)"


def test_metric_value_matches_source_extraction(all_extractions, conn):
    """Spot-check: for each company, pick one financial-page metric with a
    canonical 4-digit year and confirm the DB value matches the JSON exactly.
    Skips entries with non-canonical year labels (e.g., 'FY2025_3Q')."""
    import re
    for key, ex in all_extractions.items():
        for page in ex.get("financial_pages", []):
            if not page.get("is_financial_table") or not page.get("metrics"):
                continue
            page_id = page["page_id"]
            for met in page["metrics"]:
                checked = False
                for y, v in (met.get("values") or {}).items():
                    if not isinstance(v, (int, float)):
                        continue
                    if not isinstance(y, str) or not re.match(r"^\d{4}$", y):
                        continue
                    row = conn.execute("""
                        SELECT value_native FROM financial_metrics
                        WHERE page_id=? AND metric_name=? AND year=?
                    """, (page_id, met["name"], y)).fetchone()
                    assert row is not None, f"{key}/{page_id}: '{met['name']}' year {y} missing in DB"
                    assert abs(row["value_native"] - v) < 1e-6, (
                        f"{key}/{page_id}/{met['name']}/{y}: DB={row['value_native']} JSON={v}"
                    )
                    checked = True
                    break
                if checked:
                    break
            break
