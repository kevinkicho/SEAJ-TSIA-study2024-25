"""Tests for the graphify-out → financials.db integration.

Verifies that:
  - the three new tables (entities, relationships, communities) are populated
  - the cross-link from companies → entities covers most financial companies
  - the cross-link references are valid (every financial_company_id resolves)
  - integrated SQL queries return non-trivial results
"""
import pytest


def test_entities_table_populated(conn):
    n = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    assert n >= 1500, f"entities table has only {n} rows (expected ~1,512)"


def test_relationships_table_populated(conn):
    n = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    assert n >= 1800, f"relationships table has only {n} rows (expected ~1,848)"


def test_communities_table_populated(conn):
    n = conn.execute("SELECT COUNT(*) FROM communities").fetchone()[0]
    assert n >= 100, f"communities table has only {n} rows (expected ~174)"


def test_cross_link_coverage(conn):
    """At least 90% of financial companies should cross-link to a graph entity."""
    n_co = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    n_linked = conn.execute("""
        SELECT COUNT(DISTINCT c.company_id)
        FROM companies c
        JOIN entities e ON e.financial_company_id = c.company_id
    """).fetchone()[0]
    rate = n_linked / max(n_co, 1)
    assert rate >= 0.90, f"only {n_linked}/{n_co} ({rate:.0%}) financial companies are cross-linked"


def test_cross_link_targets_resolve(conn):
    """Every entities.financial_company_id must point to an existing companies row."""
    bad = conn.execute("""
        SELECT e.entity_id, e.financial_company_id
        FROM entities e
        LEFT JOIN companies c ON c.company_id = e.financial_company_id
        WHERE e.financial_company_id IS NOT NULL AND c.company_id IS NULL
    """).fetchall()
    assert not bad, f"dangling cross-link references: {bad[:5]}"


def test_relationship_endpoints_resolve(conn):
    """Every relationship's source and target must be a real entity."""
    bad = conn.execute("""
        SELECT r.id, r.source_entity, r.target_entity
        FROM relationships r
        LEFT JOIN entities es ON es.entity_id = r.source_entity
        LEFT JOIN entities et ON et.entity_id = r.target_entity
        WHERE es.entity_id IS NULL OR et.entity_id IS NULL
        LIMIT 10
    """).fetchall()
    assert not bad, f"dangling relationship endpoints: {bad}"


def test_integrated_query_returns_results(conn):
    """The canonical integrated query (financials + community) must return data."""
    rows = conn.execute("""
        SELECT c.label, fm.canonical_name, fm.year, fm.value_native, e.community
        FROM companies c
        JOIN entities e ON e.financial_company_id = c.company_id
        JOIN financial_metrics fm ON fm.company_id = c.company_id
        WHERE fm.canonical_name = 'revenue'
          AND e.community IS NOT NULL
        LIMIT 20
    """).fetchall()
    assert len(rows) >= 10, f"integrated query returned only {len(rows)} rows"


def test_supply_chain_edges_query(conn):
    """Companies with financials should also have at least some structural relationships
    in the main graph (produces, supplies_to, etc.)."""
    rows = conn.execute("""
        SELECT c.label, COUNT(r.id) AS n_edges
        FROM companies c
        JOIN entities e ON e.financial_company_id = c.company_id
        LEFT JOIN relationships r ON r.source_entity = e.entity_id OR r.target_entity = e.entity_id
        GROUP BY c.label
        HAVING n_edges > 0
    """).fetchall()
    assert len(rows) >= 30, f"only {len(rows)} financial companies have any main-graph edges"


def test_indexes_on_integrated_tables(conn):
    expected = {
        "idx_entities_type", "idx_entities_community",
        "idx_entities_norm_label", "idx_entities_financial_link",
        "idx_rel_source", "idx_rel_target", "idx_rel_relation",
    }
    have = {r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index'"
    ).fetchall()}
    missing = expected - have
    assert not missing, f"missing integrated-table indexes: {missing}"
