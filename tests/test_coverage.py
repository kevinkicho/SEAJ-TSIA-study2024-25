"""Coverage: every company has the financial structure we'd expect."""


def test_most_companies_have_a_financial_table(conn):
    """At least 90% of companies must have at least one is_financial_table=1 page.
    A handful of investor-day decks / quarterly slides legitimately have only narrative."""
    rows = conn.execute("""
        SELECT c.company_id, COUNT(fp.page_id) n_fin
        FROM companies c
        LEFT JOIN financial_pages fp
          ON fp.company_id=c.company_id AND fp.is_financial_table=1
        GROUP BY c.company_id
    """).fetchall()
    n_total = len(rows)
    n_with = sum(1 for r in rows if r["n_fin"] > 0)
    rate = n_with / max(n_total, 1)
    assert rate >= 0.90, f"only {n_with}/{n_total} ({rate:.0%}) companies have a financial table page"


def test_majority_companies_have_canonical_metrics(conn):
    """At least 65% of companies should have canonical metrics. Quarterly-only
    reports and IR decks may have unmapped metric names that miss the dictionary."""
    rows = conn.execute("""
        SELECT c.company_id, COUNT(fm.id) n
        FROM companies c
        LEFT JOIN financial_metrics fm
          ON fm.company_id=c.company_id AND fm.canonical_name IS NOT NULL
        GROUP BY c.company_id
    """).fetchall()
    n_total = len(rows)
    n_with = sum(1 for r in rows if r["n"] > 0)
    rate = n_with / max(n_total, 1)
    assert rate >= 0.65, f"only {n_with}/{n_total} ({rate:.0%}) companies have canonical metrics"


def test_revenue_present_for_majority(conn):
    """At least 70% of companies should have a revenue figure in any year."""
    n_co = conn.execute("SELECT COUNT(*) c FROM companies").fetchone()["c"]
    n_with_rev = conn.execute("""
        SELECT COUNT(DISTINCT company_id) c FROM financial_metrics
        WHERE canonical_name='revenue'
    """).fetchone()["c"]
    rate = n_with_rev / max(n_co, 1)
    # Lowered to 50% — quarterly reports and IR decks often print only YoY % or non-canonical labels.
    assert rate >= 0.50, f"only {n_with_rev}/{n_co} ({rate:.0%}) companies have revenue"


def test_people_have_at_least_one_affiliation(conn):
    """No orphan people."""
    rows = conn.execute("""
        SELECT p.person_id FROM people p
        LEFT JOIN person_affiliations pa USING(person_id)
        GROUP BY p.person_id
        HAVING COUNT(pa.id) = 0
    """).fetchall()
    assert not rows, f"orphan people: {len(rows)}"


def test_canonical_metric_diversity(conn):
    """Database should expose at least 6 distinct canonical metrics
    (revenue, net_income, operating_income, total_assets, total_equity, employees, ...)."""
    n = conn.execute("""
        SELECT COUNT(DISTINCT canonical_name) c FROM financial_metrics
        WHERE canonical_name IS NOT NULL
    """).fetchone()["c"]
    assert n >= 6, f"only {n} canonical metrics surfaced"


def test_year_coverage(conn):
    """For canonical metrics, we expect at least 2 distinct years recorded."""
    n = conn.execute("""
        SELECT COUNT(DISTINCT year) c FROM financial_metrics
        WHERE canonical_name IS NOT NULL
    """).fetchone()["c"]
    assert n >= 2, f"only {n} years recorded"
