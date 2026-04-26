"""Shared fixtures for the financial-graph test suite."""
import json, sqlite3, sys
from pathlib import Path
import pytest

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"

# Make scripts/ importable for tests that need build_merged_graph helpers
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="session")
def db_path() -> Path:
    p = GF / "financials.db"
    if not p.exists():
        pytest.skip(f"db missing: {p}")
    return p


@pytest.fixture(scope="session")
def conn(db_path: Path):
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


@pytest.fixture(scope="session")
def graph_financial() -> dict:
    p = GF / "graph-financial.json"
    if not p.exists():
        pytest.skip(f"graph-financial.json missing")
    return json.loads(p.read_text())


@pytest.fixture(scope="session")
def fx_rates() -> dict:
    p = GF / "fx_rates.json"
    return json.loads(p.read_text())


@pytest.fixture(scope="session")
def all_extractions() -> dict:
    """Map of company_key → extraction dict, unified shape."""
    out = {}
    tsmc_fin = GF / "tsmc/tsmc_financials.json"
    tsmc_ppl = GF / "tsmc/tsmc_people.json"
    if tsmc_fin.exists() and tsmc_ppl.exists():
        fin = json.loads(tsmc_fin.read_text())
        ppl = json.loads(tsmc_ppl.read_text())
        out["tsmc"] = {
            "financial_pages": fin["pages"],
            "people_pages": ppl["pages"],
            "currency_default": "TWD",
        }
    for d in GF.iterdir():
        if not d.is_dir():
            continue
        ext = d / f"{d.name}_extraction.json"
        if ext.exists():
            out[d.name] = json.loads(ext.read_text())
    return out
