#!/usr/bin/env python3.12
"""Integrate graphify-out's qualitative graph into financials.db.

Adds three tables to the existing SQLite store:
    entities          — every node from graphify-out/graph.json (1,512 rows)
    relationships     — every edge (1,848 rows)
    communities       — the 174 community clusters

Also adds a `financial_company_id` column to `entities` that cross-links
each company entity to its matching `companies.company_id` row in the
financial layer (where a match exists).

Cross-linking strategy:
    1. Exact label match (lowercased)
    2. Norm-label match (alphanumeric + underscores)
    3. Substring match in either direction (with length guard)
    4. Curated overrides (the 10 baseline companies)

Idempotent: drops + recreates the three tables on every run; preserves the
financial-layer tables untouched.
"""
from __future__ import annotations
import json, re, sqlite3, sys
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
DB_PATH = ROOT / "graphify-financial" / "financials.db"
# Prefer the enriched graph (main + financial-briefs merged) if it exists.
# Falls back to the original main graph.
MAIN_GRAPH = ROOT / "graphify-out" / "graph-enriched.json"
if not MAIN_GRAPH.exists():
    MAIN_GRAPH = ROOT / "graphify-out" / "graph.json"


# ---------- schema ----------

SCHEMA = """
DROP TABLE IF EXISTS entities;
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS communities;

CREATE TABLE entities (
    entity_id            TEXT PRIMARY KEY,
    label                TEXT NOT NULL,
    norm_label           TEXT,
    entity_type          TEXT,
    file_type            TEXT,
    country              TEXT,
    industry             TEXT,
    community            INTEGER,
    source_file          TEXT,
    source_location      TEXT,
    confidence           REAL,
    description          TEXT,
    attributes_json      TEXT,
    financial_company_id TEXT,
    FOREIGN KEY (financial_company_id) REFERENCES companies(company_id)
);

CREATE TABLE relationships (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity   TEXT NOT NULL,
    target_entity   TEXT NOT NULL,
    relation        TEXT,
    weight          REAL,
    confidence      REAL,
    source_file     TEXT,
    notes           TEXT,
    FOREIGN KEY (source_entity) REFERENCES entities(entity_id),
    FOREIGN KEY (target_entity) REFERENCES entities(entity_id)
);

CREATE TABLE communities (
    community_id    INTEGER PRIMARY KEY,
    n_members       INTEGER,
    sample_labels   TEXT
);

CREATE INDEX idx_entities_type           ON entities (entity_type);
CREATE INDEX idx_entities_community      ON entities (community);
CREATE INDEX idx_entities_norm_label     ON entities (norm_label);
CREATE INDEX idx_entities_financial_link ON entities (financial_company_id);
CREATE INDEX idx_rel_source              ON relationships (source_entity);
CREATE INDEX idx_rel_target              ON relationships (target_entity);
CREATE INDEX idx_rel_relation            ON relationships (relation);
"""


# Manual cross-link overrides — handle cases where the graphify-financial company_id
# doesn't auto-match the graphify-out entity_id. For each:
#   financial_company_id (in companies table) → graphify-out entity_id (in nodes)
MANUAL_LINKS = {
    "tsmc": "tsmc",
    "umc": "umc",
    "amat": "applied_materials",
    "wpg": "wpg_holdings",
    "ase": "ase_technology_holding",
    "alcor": "alcor_micro",
    "egis": "egis",
    "vis": "vis",
    "itri": "itri",
    "medipal": "medipal_holdings",
    "phison_2024_annual_report": "phison",
    "mediatek_2024_english_annual_report": "mediatek",
    "himax_2024_annual_report": "himax_technologies",
    "lam_research_corp_2025_v1_annual_report_2025": "lam_research",
    "klac_2025_annual_report_bookmarked": "kla",
    "annual_report_2024_asm_final": "asm_international",
    "asm_2025_annual_report": "asm_international",
    "annual_report_2025_shinetsu": "shin_etsu_chemical",
    "integrated_report_lasertec_2025": "lasertec",
    "e_all_iar2025_advantest_annual_report_2025": "advantest",
    "e_accretech_2025": "accretech_tokyo_seimitsu",
    "report_2025_shimadzu": "shimadzu",
    "report_2025_a3_en_jeol": "jeol",
    "ckd_all_web": "ckd_corporation",
    "00_uacj_integrated_report_2025": "uacj",
    "00_shibuara_integrated_report_2025": "shibaura_mechatronics",
    "int25_all_en_1_ebara_corporation_2024": "ebara",
    "marumae_annual_report_2025en": "marumae",
    "report_2025_a4_eng_rikken_keiki_2025": "rikken_keiki",
    "results_for_the_fiscal_year_ended_march_2025_rikken_keiki": "rikken_keiki",
    "report_2025_all_lintec": "lintec",
    "ir_full_nagase_integrated_report_2025": "nagase",
    "ardentech_annual_report_2024_esg": "ardentec_corporation",
    "chipmos_taiwan_annual_report_2024_en_ir_year_1820663809": "chipmos_technologies",
    "delta_electronics_annual_report_2024": "delta_electronics",
    "richwave_annual_report_2024": "richwave",
    "topco_global_annual_2024_annual_113eng": "topco_global",
    "marketech_annual_report_2024": "marketech_international",
    "mic_taiwan_annual_report_2024": "mic",
    "psmc_annual_reports_2024_en": "psmc_powerchip",
    "2024_win_annual_report": "win_semiconductors",
    "ap_memory_annual_report_2024": "ap_memory",
    "ememory_annual_report_2024": "ememory",
    "m31_annual_report_2024_113m31_eng_1": "m31_technology",
    "2024_annual_report_realtek": "realtek",
    "2024_annual_report": "nanya_technology",
    "leatec_fine_ceramics_2024annual_report": "leatec_fine_ceramics",
    "csun_annual_report_2024_113_v4_20251121_p_21_48_50": "csun_manufacturing",
    "creating_nanotech_2025cnt_pdfc_7917259_132442_3461176": "creating_nanotech",
    "favite_annual_report_2024_113_eng": "favite",
    "favite_annual_report_2024_113": "favite",
    "gallant_annual_report_2024_20250331_annual_repor_en": "gallant_mm",
    "gallant_annual_report_2024": "gallant_mm",
    "mic_taiwan_annual_report_2024": None,
    "kyec_2449_4q25_investor_update_english": "kyec",
    "sigurd_annual_report_2024_113q4_copy": "sigurd",
    "spirox_annual_report_2024_113": "spirox",
    "zdtco_annual_report_en_revised": "zdtco",
    "113_114_08_15_916123_taiwan_mask_company_annual_report_2024": "taiwan_mask_corp",
    "114_all_en_orient_semiconductor_2024_annual_report": "orient_semiconductor_ose",
    "26third_all_e_nikon_3q_2025_result": "nikon",
    "phase7_e_canon_presentation_jan_2026": "canon_inc",
    "conf2025e_canon_fy2025_result": "canon_inc",
    "daifuku_presentation": "daifuku",
    "daitron_e_2025q4_fr": "daitron",
    "01_25_3q_results_e": "iwatani",
    "02_25_3q_e": "iwatani",
    "2024_shinagawa_update_20240530": "shinagawa_refractories",
    "2024annual_report_seino": "seino_holdings",
    "fubon_financial_annual_report_2024": "fubon_financial",
    "hcl_tech_annual_report_2024_25": "hcl_technologies",
    "itochu_ar2025e": "itochu",
    "dbjintegratedreport2025": "dbj",
    "misumi_report_2025_english_all_ver_2": "misumi_group",
    "jsr_annual_report_2024_2025_e_all": "jsr",
    "organo_financial_results_for_first_half_of_fiscal_year_endin": "organo",
    "all_analyst_day_2025_ir_site_new_teradyne_investor_day_mar_2": "teradyne",
    "ec_q4_25_slides_feb2026": "teradyne",
    "weltrend_2024_sustainability_report": "weltrend",
    "megawin_taiwan_annual_report_2024_chinese_113": "megawin_technology",
    "epis_news_20240701_annual_report_2024": "episil_technologies",
    "fuji_electric_ar2025_02_02_e": "fuji_electric",
    "fuji_electric_ar2025_02_04_e": "fuji_electric",
    "ysut_snk_integrated_report_2025": "snk_holdings",
    "index_01_sanki_2023": "sanki",
    "sgs_2025_integrated_report_en": "sgs",
    "hy_report_2025": "inficon",
    "interaction_jp_medium_term_business_plan_2024_2028": "interaction",
    "panasonic_industry_ir_pre2024_pid_e": "panasonic_industry",
    "ardentech_annual_report_2024": "ardentec_corporation",
    "ajinomoto_fine_inc_abf_presentation": "ajinomoto_fine_techno_aft",
    "2024_annual_report_2": "itri",
    "4q25_investor_en_final_windbond_2025": "winbond",
    "phison_2024_annual_report": "phison",
    "2025q3_balance_sheet": None,  # generic balance sheet, no entity match
    "dar2020_disco_annual_report_2020": "disco",
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (s or "").lower().strip()).strip("_")


def build_entity_index(graph: dict) -> dict[str, dict]:
    """Return {entity_id: node_dict} indexed by id."""
    return {n["id"]: n for n in graph["nodes"]}


def find_match(financial_co: dict, entity_index: dict, manual: dict) -> str | None:
    """Try to find a graphify-out entity_id matching this company. Returns id or None."""
    cid = financial_co["company_id"]
    label = financial_co.get("label") or ""

    if cid in manual:
        target = manual[cid]
        if target is None:
            return None
        if target in entity_index:
            return target
        # Fall through if manual mapping points to a non-existent entity

    nlabel = norm(label)
    # Try exact id match
    if nlabel in entity_index:
        return nlabel
    # Norm-label match
    for eid, e in entity_index.items():
        if e.get("type") != "company":
            continue
        if norm(e.get("label", "")) == nlabel:
            return eid
        if norm(e.get("norm_label", "")) == nlabel:
            return eid
    # Substring match (length guard: shorter side >= 4 chars)
    for eid, e in entity_index.items():
        if e.get("type") != "company":
            continue
        elabel = norm(e.get("label", ""))
        if not elabel or not nlabel:
            continue
        if len(nlabel) >= 4 and len(elabel) >= 4:
            if nlabel in elabel or elabel in nlabel:
                return eid
    return None


def main():
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}", file=sys.stderr)
        sys.exit(1)
    if not MAIN_GRAPH.exists():
        print(f"Main graph not found: {MAIN_GRAPH}", file=sys.stderr)
        sys.exit(1)

    graph = json.loads(MAIN_GRAPH.read_text())
    nodes = graph["nodes"]
    edges = graph.get("links") or graph.get("edges") or []

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # ---- entities ----
    entity_index = build_entity_index(graph)
    for n in nodes:
        # Pull commonly-used fields, dump the rest into attributes_json
        common_keys = {
            "id", "label", "norm_label", "type", "file_type", "country",
            "industry", "community", "source_file", "source_location",
            "confidence", "description",
        }
        extra = {k: v for k, v in n.items() if k not in common_keys}
        conn.execute(
            """INSERT OR REPLACE INTO entities
               (entity_id, label, norm_label, entity_type, file_type, country,
                industry, community, source_file, source_location, confidence,
                description, attributes_json, financial_company_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                n["id"], n.get("label", ""), n.get("norm_label"),
                n.get("type"), n.get("file_type"), n.get("country"),
                n.get("industry"), n.get("community"),
                n.get("source_file"), n.get("source_location"),
                n.get("confidence"), n.get("description"),
                json.dumps(extra, ensure_ascii=False) if extra else None,
                None,  # financial_company_id, fill in below
            ),
        )

    # ---- relationships ----
    for e in edges:
        conn.execute(
            """INSERT INTO relationships
               (source_entity, target_entity, relation, weight, confidence,
                source_file, notes)
               VALUES (?,?,?,?,?,?,?)""",
            (
                e.get("source"), e.get("target"), e.get("relation"),
                e.get("weight"), e.get("confidence") or e.get("confidence_score"),
                e.get("source_file"), e.get("notes") or e.get("rationale"),
            ),
        )

    # ---- communities ----
    comm_groups: dict[int, list[str]] = {}
    for n in nodes:
        c = n.get("community")
        if c is None:
            continue
        comm_groups.setdefault(c, []).append(n.get("label", n["id"]))
    for cid, labels in sorted(comm_groups.items()):
        conn.execute(
            "INSERT INTO communities (community_id, n_members, sample_labels) VALUES (?, ?, ?)",
            (cid, len(labels), " | ".join(sorted(labels)[:8])),
        )

    # ---- cross-link financial_company_id ----
    n_linked = 0
    n_total = 0
    unlinked = []
    for r in conn.execute("SELECT company_id, label FROM companies").fetchall():
        n_total += 1
        co = {"company_id": r[0], "label": r[1]}
        match = find_match(co, entity_index, MANUAL_LINKS)
        if match:
            conn.execute(
                "UPDATE entities SET financial_company_id=? WHERE entity_id=?",
                (co["company_id"], match),
            )
            n_linked += 1
        else:
            unlinked.append(co["company_id"])

    conn.commit()

    n_entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    n_rels = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    n_comms = conn.execute("SELECT COUNT(*) FROM communities").fetchone()[0]
    print(f"Loaded {n_entities} entities, {n_rels} relationships, {n_comms} communities into financials.db")
    print(f"Cross-linked {n_linked}/{n_total} financial companies to graph entities")
    if unlinked:
        print(f"\nUnlinked ({len(unlinked)}):")
        for u in unlinked[:20]:
            print(f"  {u}")

    # Sample queries demonstrating the integration
    print("\n=== Sample integrated query: financial companies with their main-graph community ===")
    for r in conn.execute("""
        SELECT c.label, e.label AS graph_label, e.community, com.n_members AS community_size
        FROM companies c
        JOIN entities e ON e.financial_company_id = c.company_id
        LEFT JOIN communities com ON com.community_id = e.community
        ORDER BY com.n_members DESC, c.label
        LIMIT 12
    """).fetchall():
        print(f"  {r[0]:35s} → graph: {r[1]:35s} community={r[2]} (size={r[3]})")

    print("\n=== Sample integrated query: relationships to/from financial companies ===")
    for r in conn.execute("""
        SELECT c.label AS company, r.relation, e.label AS related_to, e.entity_type
        FROM companies c
        JOIN entities ec ON ec.financial_company_id = c.company_id
        JOIN relationships r ON r.source_entity = ec.entity_id
        JOIN entities e ON e.entity_id = r.target_entity
        ORDER BY c.label
        LIMIT 12
    """).fetchall():
        print(f"  {r[0]:25s} --{r[1]:20s}--> {r[2][:35]:35s} ({r[3]})")

    conn.close()


if __name__ == "__main__":
    main()
