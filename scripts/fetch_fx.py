#!/usr/bin/env python3.12
"""Fetch live FX rates from frankfurter.dev (+ open.er-api.com for TWD).

Frankfurter follows ECB and does not publish TWD; we fall back to
open.er-api.com (free, no key) for TWD only. Rates are written as
USD-per-unit (so multiply native value × rate → USD).
"""
import json, urllib.request, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
OUT = ROOT / "graphify-financial" / "fx_rates.json"

NEEDED = ["JPY", "TWD", "USD"]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "graphify-financial/1.0 (kevin@local)"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)

def main():
    out = {"fetched_at": datetime.now(timezone.utc).isoformat(), "rates_usd_per_unit": {}, "sources": {}}

    # Frankfurter: USD base → rates per USD for many currencies
    frank = get("https://api.frankfurter.dev/v1/latest?base=USD")
    frank_rates = frank.get("rates", {})
    frank_date = frank.get("date")
    out["sources"]["frankfurter"] = {"url": "https://api.frankfurter.dev", "date": frank_date}

    # USD itself
    out["rates_usd_per_unit"]["USD"] = 1.0
    out["sources"]["USD"] = "constant"

    # JPY (from frankfurter)
    if "JPY" in frank_rates:
        # frankfurter "rates": 1 USD = N JPY → USD per JPY = 1/N
        out["rates_usd_per_unit"]["JPY"] = 1.0 / frank_rates["JPY"]
        out["sources"]["JPY"] = f"frankfurter.dev ({frank_date})"

    # TWD: not on frankfurter (ECB doesn't publish TWD). Fall back.
    er = get("https://open.er-api.com/v6/latest/USD")
    er_rates = er.get("rates", {})
    er_date = er.get("time_last_update_utc")
    out["sources"]["open.er-api"] = {"url": "https://open.er-api.com", "date": er_date}
    if "TWD" in er_rates:
        out["rates_usd_per_unit"]["TWD"] = 1.0 / er_rates["TWD"]
        out["sources"]["TWD"] = f"open.er-api.com ({er_date}) — frankfurter does not cover TWD"

    # Verify all needed currencies have a rate
    missing = [c for c in NEEDED if c not in out["rates_usd_per_unit"]]
    if missing:
        print(f"[ERROR] missing: {missing}", file=sys.stderr)
        sys.exit(1)

    OUT.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT}")
    for c, r in out["rates_usd_per_unit"].items():
        print(f"  1 {c} = ${r:.6f} USD  ({out['sources'].get(c, '?')})")

if __name__ == "__main__":
    main()
