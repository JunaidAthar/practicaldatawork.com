"""Helpers for HRSA 340B OPAIS public exports (Contract Pharmacy search export)."""
import re
from pathlib import Path

import pandas as pd


def _norm(s) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


def load_contract_pharmacies(path: str | Path) -> pd.DataFrame:
    """Load an OPAIS 'Contract Pharmacy List Export' (.xlsx).

    The export has a title block and a two-row header; the column header row is the one
    starting with '340B ID'. Pharmacy columns follow 'Pharmacy Name'.
    """
    raw = pd.read_excel(path, header=None, dtype=str)
    hdr = raw.index[raw.iloc[:, 0].astype(str).str.strip() == "340B ID"][0]
    cols = [str(c).strip() for c in raw.iloc[hdr]]
    df = raw.iloc[hdr + 1:].reset_index(drop=True)
    df.columns = cols
    p = cols.index("Pharmacy Name")
    out = pd.DataFrame({
        "covered_entity_id": df.iloc[:, 0],
        "entity_name": df["Entity Name"],
        "pharmacy_name": df.iloc[:, p],
        "pharmacy_opais_id": df.iloc[:, p + 2],
        "pharmacy_address": df.iloc[:, p + 3],
        "pharmacy_city": df.iloc[:, p + 6],
        "pharmacy_state": df.iloc[:, p + 7],
        "pharmacy_zip": df.iloc[:, p + 8].astype(str).str[:5],
        "contract_begin": df.iloc[:, p + 10],
        "contract_term": df.iloc[:, p + 12],
    })
    return out.dropna(subset=["pharmacy_name"])


def find_pharmacy(cp: pd.DataFrame, name: str, zip5: str | None = None) -> pd.DataFrame:
    """Rows where the pharmacy name contains `name` (normalized) and, if given, the ZIP matches."""
    key = _norm(name)
    hit = cp[cp["pharmacy_name"].map(_norm).str.contains(key, regex=False)]
    if zip5:
        hit = hit[hit["pharmacy_zip"] == str(zip5)[:5]]
    return hit


def has_active_contracts(cp: pd.DataFrame, name: str, zip5: str | None = None, as_of=None) -> bool:
    """True if any matching contract has no termination date or terminates after `as_of`."""
    hit = find_pharmacy(cp, name, zip5)
    if hit.empty:
        return False
    as_of = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    term = pd.to_datetime(hit["contract_term"], errors="coerce")
    return bool((term.isna() | (term > as_of)).any())
