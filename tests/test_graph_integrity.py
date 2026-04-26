"""Graph integrity: nodes/edges in graph-financial.json reference real entities."""


def test_graph_has_companies_and_people(graph_financial):
    types = {n["type"] for n in graph_financial["nodes"]}
    assert "company" in types, "no company nodes"
    assert "person" in types, "no person nodes"


def test_no_dangling_edges(graph_financial):
    node_ids = {n["id"] for n in graph_financial["nodes"]}
    bad = []
    for e in graph_financial.get("links", []):
        if e["source"] not in node_ids:
            bad.append(("source", e["source"]))
        if e["target"] not in node_ids:
            bad.append(("target", e["target"]))
    assert not bad, f"dangling edge endpoints: {bad[:5]}"


def test_company_nodes_match_db(graph_financial, conn):
    db_companies = {r["company_id"] for r in conn.execute("SELECT company_id FROM companies")}
    graph_companies = {
        n["id"].removeprefix("company_") for n in graph_financial["nodes"] if n["type"] == "company"
    }
    assert db_companies == graph_companies, (
        f"company set mismatch — DB only: {db_companies - graph_companies}, "
        f"graph only: {graph_companies - db_companies}"
    )


def test_majority_company_nodes_have_canonical_metrics(graph_financial):
    """At least 65% of company nodes should expose canonical metrics; quarterly
    decks and IR slides may have unmapped metric labels."""
    bad = []
    co_total = 0
    for n in graph_financial["nodes"]:
        if n["type"] != "company":
            continue
        co_total += 1
        m = n.get("metrics_canonical") or {}
        if not m:
            bad.append(n["id"])
    rate = (co_total - len(bad)) / max(co_total, 1)
    assert rate >= 0.65, f"only {co_total - len(bad)}/{co_total} ({rate:.0%}) company nodes have canonical metrics"


def test_fx_in_graph_metadata(graph_financial):
    g = graph_financial.get("graph", {})
    fx = g.get("fx_to_usd")
    assert fx, "graph.fx_to_usd missing"
    for c in ("USD", "TWD", "JPY"):
        assert c in fx, f"FX rate missing for {c}"


def test_person_nodes_have_primary_company(graph_financial):
    bad = []
    for n in graph_financial["nodes"]:
        if n["type"] != "person":
            continue
        if not n.get("primary_company"):
            bad.append(n["id"])
    assert not bad, f"person nodes missing primary_company: {bad[:5]}"
