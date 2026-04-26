#!/usr/bin/env python3.12
"""Normalize year labels from extracted financial data.

Common labels in the corpus:
    "2024"             → year=2024, period="FY"   (calendar year)
    "FY2024"           → year=2024, period="FY"
    "FY3/2024"         → year=2024, period="FY3"  (Japanese fiscal year ending March 2024)
    "2024-12-31"       → year=2024, period="as_of"
    "FY2024_3Q"        → year=2024, period="Q3"
    "FY2025_3Q"        → year=2025, period="Q3"
    "4Q25"             → year=2025, period="Q4"
    "3Q25"             → year=2025, period="Q3"
    "Q3 2025"          → year=2025, period="Q3"
    "2025_9M"          → year=2025, period="9M"   (9-month interim)
    "2025_H1"          → year=2025, period="H1"
    "FY2026/3 Forecast" → year=2026, period="FY3", forecast=True
    "FY2025 Forecast"  → year=2025, period="FY", forecast=True

Returns (year, period, is_forecast). year is a 4-digit string; period is one of
{"FY","FY3","Q1","Q2","Q3","Q4","H1","H2","9M","as_of","unknown"}; is_forecast
is True when the label includes "forecast"/"plan"/"target".
"""
from __future__ import annotations
import re

PATTERNS = [
    # Date as_of (balance-sheet headers): YYYY-MM-DD or YYYY/MM/DD
    (re.compile(r"^(\d{4})[-/]\d{2}[-/]\d{2}"), "as_of"),
    # 4-digit calendar year only
    (re.compile(r"^(\d{4})$"), "FY"),
    # FY-prefixed plain year: FY2024 / FY 2024
    (re.compile(r"^FY\s*(\d{4})$", re.I), "FY"),
    # Japanese fiscal year notation: FY3/2024 OR FY2024/3 (year ending March 2024)
    (re.compile(r"^FY\s*\d/(\d{4})$", re.I), "FY3"),
    (re.compile(r"^FY\s*(\d{4})/\d$", re.I), "FY3"),
    # FY year + quarter: FY2024_3Q, FY2024 3Q, FY2024-3Q
    (re.compile(r"^FY\s*(\d{4})[\s_\-]+([1-4])Q$", re.I), "Q?"),
    (re.compile(r"^FY\s*(\d{4})[\s_\-]+Q([1-4])$", re.I), "Q?"),
    # NQYY style: 4Q25, 3Q25, 1Q24
    (re.compile(r"^([1-4])Q\s*(\d{2})$"), "Q?"),
    # NQ YYYY: "Q3 2025"
    (re.compile(r"^Q([1-4])\s*(\d{4})$", re.I), "Q?"),
    # Half-year + year: 2025_H1, H1 2025
    (re.compile(r"^(\d{4})[\s_\-]+H([12])$"), "H?"),
    (re.compile(r"^H([12])\s*(\d{4})$", re.I), "H?"),
    # 9-month / 6-month / 3-month interim: 2025_9M
    (re.compile(r"^(\d{4})[\s_\-]+(\d{1,2})M$", re.I), "?M"),
    # Year + Forecast/Plan/Target qualifier: "FY2026 Forecast" handled by stripping the qualifier first
    # (handled in normalize() below)
]

FORECAST_RE = re.compile(r"\b(forecast|forecasts|plan|target|projection|guidance|estimate|initial_plan|previous_forecast|current_forecast)\b", re.I)
ROC_RE = re.compile(r"^民國?\s*(\d{2,3})$")
# Strip miscellaneous qualifiers that don't affect year/period (e.g., "Actual", "Full Year")
NOISE_RE = re.compile(r"\b(actual|full[\s_-]year|consolidated|company[\s_-]wide|reported|adjusted)\b", re.I)
# Patterns to identify non-year columns we should skip silently
NON_YEAR_RE = re.compile(r"^(progress[\s_-]?pct|yoy|growth|change|delta|variance|ratio)$", re.I)
# Month-name → fiscal-end mapping (e.g., "2025_Mar" = FY3 ending March 2025)
MONTH_TO_PERIOD = {"jan": "FY1", "feb": "FY2", "mar": "FY3", "apr": "FY4",
                   "may": "FY5", "jun": "FY6", "jul": "FY7", "aug": "FY8",
                   "sep": "FY9", "oct": "FY10", "nov": "FY11", "dec": "FY"}
MONTH_RE = re.compile(r"^(\d{4})[\s_\-]+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", re.I)
# YYYY/M format with extra suffix: FY03/2025_Actual, FY03/2026
FY_NM_YYYY_RE = re.compile(r"^FY\s*(\d{1,2})/(\d{4})$", re.I)
FY_YYYY_NM_RE = re.compile(r"^FY\s*(\d{4})/(\d{1,2})$", re.I)
# Date-as-of with month name: "Dec_31_2025"
DATE_MONTH_RE = re.compile(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s_\-]+\d{1,2}[\s_\-]+(\d{4})$", re.I)
# Half-year + FY: "FY2026/3 1H", "FY2026/3 2H", "2024_1H_FY03/2025"
H_PLUS_FY_RE = re.compile(r"FY\s*\d{0,4}/?\d?\s*([12])H$", re.I)
H_AT_END_RE = re.compile(r"(?:^|[\s_])(\d{4})[\s_]+([12])H(?:[\s_]|$)", re.I)


def normalize(label: str) -> tuple[str | None, str, bool]:
    """Return (year_4digit_str, period, is_forecast).

    year is None if no 4-digit year can be extracted.
    """
    if not isinstance(label, str):
        return (None, "unknown", False)
    s = label.strip()
    if not s:
        return (None, "unknown", False)

    # Skip non-year column headers (Progress_pct, YoY, etc.)
    if NON_YEAR_RE.match(s):
        return (None, "non_year_column", False)

    # Order matters: convert _/- to spaces FIRST so word-boundary regexes match noise tokens
    # (since _ is a word character, \b doesn't fire between _ and a letter)
    s_clean = re.sub(r"[_\-]+", " ", s)
    is_forecast = bool(FORECAST_RE.search(s_clean))
    s_clean = FORECAST_RE.sub("", s_clean)
    # Also strip "Initial", "Previous", "Current" qualifiers (these accompany Plan/Forecast)
    s_clean = re.sub(r"\b(initial|previous|current|revised|preliminary|final)\b", "", s_clean, flags=re.I)
    s_clean = NOISE_RE.sub("", s_clean)
    s_clean = re.sub(r"\s+", " ", s_clean).strip(" _-")

    # Half-year-with-fiscal-year combos: 1H/2H qualifier ending FY-pattern
    m_h = H_PLUS_FY_RE.search(s_clean)
    if m_h:
        # Find the year inside FY...
        ym = re.search(r"(\d{4})", s_clean)
        if ym:
            return (ym.group(1), f"H{m_h.group(1)}", is_forecast)

    m_h2 = H_AT_END_RE.search(" " + s_clean + " ")
    if m_h2:
        return (m_h2.group(1), f"H{m_h2.group(2)}", is_forecast)

    # FY03/2025 = fiscal year ending March 2025
    m_fy = FY_NM_YYYY_RE.match(s_clean)
    if m_fy:
        month = int(m_fy.group(1))
        return (m_fy.group(2), f"FY{month}" if month != 12 else "FY", is_forecast)

    # FY2025/3 = fiscal year ending March 2025 (alt notation)
    m_fy2 = FY_YYYY_NM_RE.match(s_clean)
    if m_fy2:
        month = int(m_fy2.group(2))
        return (m_fy2.group(1), f"FY{month}" if month != 12 else "FY", is_forecast)

    # YYYY_<month> e.g., 2025 Mar, 2025 Dec
    m_m = MONTH_RE.match(s_clean)
    if m_m:
        month = m_m.group(2).lower()
        return (m_m.group(1), MONTH_TO_PERIOD.get(month, "FY"), is_forecast)

    # Month_DD_YYYY date format
    m_d = DATE_MONTH_RE.match(s_clean)
    if m_d:
        return (m_d.group(2), "as_of", is_forecast)

    # ROC date (民國113 = 2024)
    roc = ROC_RE.match(s_clean)
    if roc:
        return (str(int(roc.group(1)) + 1911), "FY", is_forecast)

    for pat, period in PATTERNS:
        m = pat.match(s_clean)
        if not m:
            continue
        groups = m.groups()
        # Decide year + period from match
        if period == "Q?":
            # First group could be year (FY pattern) or quarter (NQ pattern)
            if len(groups[0]) == 4 or (len(groups) > 1 and len(groups[1]) == 1):
                if len(groups[0]) == 4:
                    year = groups[0]
                    q = groups[1]
                else:
                    q = groups[0]
                    year = groups[1]
                    if len(year) == 2:
                        year = "20" + year
            else:
                year = groups[1] if len(groups[1]) == 4 else "20" + groups[1]
                q = groups[0]
            return (year, f"Q{q}", is_forecast)
        if period == "H?":
            # Either (year, half) or (half, year)
            a, b = groups
            if len(a) == 4:
                return (a, f"H{b}", is_forecast)
            return (b, f"H{a}", is_forecast)
        if period == "?M":
            year, months = groups
            return (year, f"{months}M", is_forecast)
        # Default: first capture is the year
        return (groups[0], period, is_forecast)

    return (None, "unknown", is_forecast)


if __name__ == "__main__":
    samples = [
        "2024", "FY2024", "FY3/2025", "2024-12-31", "FY2024_3Q",
        "4Q25", "Q3 2025", "2025_9M", "FY2026/3 Forecast",
        "FY2025 Forecast", "民國113", "fy2025", "2024/12/31",
        "1Q24", "H1 2025", "2025_H1", "garbage",
    ]
    for s in samples:
        y, p, f = normalize(s)
        print(f"  {s!r:25s}  → year={y!r}  period={p!r}  forecast={f}")
