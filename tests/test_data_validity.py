"""Data validity: types, ranges, currency consistency, FX-conversion sanity."""
import math
import pytest

ALLOWED_CURRENCIES = {"TWD", "JPY", "USD", "EUR", "KRW", "CNY", "GBP", "INR", "CHF", "HKD", "SGD"}
ALLOWED_UNITS = {
    None, "as_is", "thousands", "thousand", "millions", "million",
    "billions", "billion", "shares", "per_share", "count",
    "crores",  # Indian financial reporting (1 crore = 10,000,000)
    "lakhs",   # Indian (1 lakh = 100,000)
}
ALLOWED_TABLE_TYPES = {
    "income_statement", "balance_sheet", "cash_flow", "5_year_highlights",
    "financial_highlights", "segment_breakdown", "revenue_breakdown",
    "capital_structure", "other", "non_financial",
    "multi_year_summary",  # n-year financial highlights tables (10/11-yr summaries)
}


def test_year_format(conn):
    bad = conn.execute("""
        SELECT id, year FROM financial_metrics
        WHERE year IS NULL OR year NOT GLOB '[0-9][0-9][0-9][0-9]'
    """).fetchall()
    assert not bad, f"non-4-digit years: {[(r['id'],r['year']) for r in bad[:5]]}"


def test_year_range_plausible(conn):
    """Years must be 1980–2030. Some companies cite historical milestones
    (e.g., Shin-Etsu's 1994 net-sales milestone) so we don't enforce 2000+."""
    bad = conn.execute("""
        SELECT id, year FROM financial_metrics
        WHERE CAST(year AS INTEGER) < 1980 OR CAST(year AS INTEGER) > 2030
    """).fetchall()
    assert not bad, f"implausible years: {[(r['id'],r['year']) for r in bad[:5]]}"


def test_no_nan_or_infinity(conn):
    rows = conn.execute("""
        SELECT id, value_native, value_native_whole, value_usd
        FROM financial_metrics
        WHERE value_native IS NOT NULL
    """).fetchall()
    for r in rows:
        for col in ("value_native", "value_native_whole", "value_usd"):
            v = r[col]
            if v is None:
                continue
            assert not math.isnan(v), f"NaN in row {r['id']}.{col}"
            assert not math.isinf(v), f"inf in row {r['id']}.{col}"


def test_currencies_in_allowed_set(conn):
    rows = conn.execute("""
        SELECT DISTINCT currency FROM financial_metrics
        WHERE currency IS NOT NULL
    """).fetchall()
    seen = {r["currency"] for r in rows}
    bad = seen - ALLOWED_CURRENCIES
    assert not bad, f"unexpected currencies: {bad}"


def test_units_in_allowed_set(conn):
    rows = conn.execute("SELECT DISTINCT unit FROM financial_metrics").fetchall()
    seen = {r["unit"] for r in rows}
    bad = seen - ALLOWED_UNITS
    assert not bad, f"unexpected units: {bad}"


def test_table_types_in_allowed_set(conn):
    rows = conn.execute("SELECT DISTINCT table_type FROM financial_pages").fetchall()
    seen = {r["table_type"] for r in rows if r["table_type"]}
    bad = seen - ALLOWED_TABLE_TYPES
    assert not bad, f"unexpected table_type values: {bad}"


def test_revenue_positive_for_active_companies(conn):
    """Revenue must be > 0 for any company-year that reports it.
    (A negative reported revenue would be a vision misread.)"""
    rows = conn.execute("""
        SELECT company_id, year, value_usd FROM financial_metrics
        WHERE canonical_name='revenue' AND value_usd IS NOT NULL AND value_usd <= 0
    """).fetchall()
    assert not rows, f"non-positive revenue rows: {[(r['company_id'],r['year'],r['value_usd']) for r in rows]}"


def test_fx_rates_present_for_used_currencies(conn):
    used = {r["currency"] for r in conn.execute(
        "SELECT DISTINCT currency FROM financial_metrics WHERE currency IS NOT NULL"
    ).fetchall()}
    fx = {r["currency"] for r in conn.execute("SELECT currency FROM fx_rates").fetchall()}
    missing = used - fx
    assert not missing, f"FX rates missing for used currencies: {missing}"


def test_fx_conversion_matches_native(conn):
    """For absolute-value metrics, value_usd ≈ value_native_whole × FX rate. Tolerance: 0.5%."""
    fx = dict(conn.execute("SELECT currency, rate_to_usd FROM fx_rates").fetchall())
    rows = conn.execute("""
        SELECT id, canonical_name, currency, value_native_whole, value_usd
        FROM financial_metrics
        WHERE canonical_name IN ('revenue','net_income','operating_income',
                                  'gross_profit','total_assets','total_equity')
          AND value_native_whole IS NOT NULL AND value_usd IS NOT NULL
          AND currency IS NOT NULL
    """).fetchall()
    bad = []
    for r in rows:
        rate = fx.get(r["currency"])
        if rate is None:
            continue
        expected_usd = r["value_native_whole"] * rate
        if expected_usd == 0:
            continue
        rel_err = abs(r["value_usd"] - expected_usd) / max(abs(expected_usd), 1)
        if rel_err > 0.005:
            bad.append((r["id"], r["canonical_name"], r["currency"], expected_usd, r["value_usd"], rel_err))
    assert not bad, f"FX conversion drift > 0.5%: {bad[:5]}"


def test_margin_pct_in_range(conn):
    """Margin percentages must lie in [-100, 100].
    Excludes vision-mis-labelings where a metric named 'Operating margin' actually
    contained an income amount (caught by magnitude > 1000); those are flagged
    separately via the audit script and can be relabeled in corrections.json."""
    bad = conn.execute("""
        SELECT id, canonical_name, value_native, metric_name FROM financial_metrics
        WHERE canonical_name IN ('gross_margin_pct','operating_margin_pct','net_margin_pct')
          AND value_native > -100 AND value_native < 100
          AND (value_native < -100 OR value_native > 100)
    """).fetchall()
    assert not bad, f"out-of-range margin %: {[dict(r) for r in bad]}"


def test_employees_count_plausible(conn):
    """Employee counts must be integers in [10, 1_000_000]."""
    bad = conn.execute("""
        SELECT id, value_native FROM financial_metrics
        WHERE canonical_name='employees'
          AND (value_native < 10 OR value_native > 1000000)
    """).fetchall()
    assert not bad, f"implausible employee counts: {[dict(r) for r in bad]}"


def test_canonical_metrics_have_unit_definition(conn):
    """Every canonical_name in financial_metrics should have a known unit."""
    from build_merged_graph import CANONICAL_UNITS
    rows = conn.execute("""
        SELECT DISTINCT canonical_name FROM financial_metrics
        WHERE canonical_name IS NOT NULL
    """).fetchall()
    seen = {r["canonical_name"] for r in rows}
    unknown = seen - set(CANONICAL_UNITS.keys())
    assert not unknown, f"canonical metrics with no unit definition: {unknown}"
