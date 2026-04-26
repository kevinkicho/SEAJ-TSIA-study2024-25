"""Performance: query latency and DB size envelopes."""
import time
import pytest


def _timed(fn, *a, **kw):
    t0 = time.perf_counter()
    out = fn(*a, **kw)
    return out, (time.perf_counter() - t0)


def test_revenue_by_company_year_query_under_100ms(conn):
    """Query latency budget: 100ms (was 50ms when DB had only the financial
    layer; now also has entities/relationships from the merged graph)."""
    _, dt = _timed(conn.execute, """
        SELECT c.label, fm.year, fm.value_usd
        FROM financial_metrics fm
        JOIN companies c USING(company_id)
        WHERE fm.canonical_name='revenue'
        ORDER BY fm.year DESC, fm.value_usd DESC
    """)
    assert dt < 0.1, f"revenue query took {dt*1000:.0f}ms"


def test_cross_board_query_under_100ms(conn):
    _, dt = _timed(conn.execute, """
        SELECT p.name, COUNT(DISTINCT pa.company_id) n
        FROM people p
        JOIN person_affiliations pa USING(person_id)
        GROUP BY p.person_id
        HAVING n > 1
    """)
    assert dt < 0.1, f"cross-board query took {dt*1000:.0f}ms"


def test_per_company_metric_lookup_under_20ms(conn):
    """Indexed lookup on (company_id, canonical_name, year) must be fast."""
    _, dt = _timed(conn.execute, """
        SELECT * FROM financial_metrics
        WHERE company_id='tsmc' AND canonical_name='revenue' AND year='2024'
    """)
    assert dt < 0.02, f"indexed lookup took {dt*1000:.0f}ms"


def test_db_size_under_100mb(db_path):
    size = db_path.stat().st_size
    assert size < 100 * 1024 * 1024, f"DB size {size:,} bytes exceeds 100 MB"


def test_full_table_scan_metrics_under_500ms(conn):
    """Sanity ceiling for the largest table."""
    _, dt = _timed(lambda: conn.execute("SELECT COUNT(*) FROM financial_metrics").fetchone())
    assert dt < 0.5, f"full count took {dt*1000:.0f}ms"
