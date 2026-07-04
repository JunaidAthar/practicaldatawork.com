"""Address normalization so signals from different datasets join on the same key.

Chicago's open datasets are fairly consistent, so a rule-based normalizer is enough
for v1. (Cook County's true parcel key is the PIN; wire that in during enrichment
for a stronger join.)
"""
from __future__ import annotations

import re

_DIRECTIONALS = {
    "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
    "NORTHEAST": "NE", "NORTHWEST": "NW", "SOUTHEAST": "SE", "SOUTHWEST": "SW",
}
_SUFFIXES = {
    "STREET": "ST", "AVENUE": "AVE", "AVE.": "AVE", "BOULEVARD": "BLVD",
    "ROAD": "RD", "DRIVE": "DR", "LANE": "LN", "COURT": "CT", "PLACE": "PL",
    "TERRACE": "TER", "PARKWAY": "PKWY", "HIGHWAY": "HWY", "SQUARE": "SQ",
    "TRAIL": "TRL", "CIRCLE": "CIR", "EXPRESSWAY": "EXPY", "PLAZA": "PLZ",
}
# Everything from these tokens onward is a unit/secondary designator — drop it.
_UNIT_SPLIT = re.compile(r"\b(APT|UNIT|STE|SUITE|FL|FLOOR|RM|ROOM|#)\b")
_PUNCT = re.compile(r"[.,]")
_WS = re.compile(r"\s+")


def normalize_address(value) -> str:
    if value is None:
        return ""
    s = str(value).upper().strip()
    if not s or s in {"NAN", "NONE"}:
        return ""
    s = _PUNCT.sub(" ", s)
    s = _UNIT_SPLIT.split(s, maxsplit=1)[0]      # cut at first unit token
    tokens = [_DIRECTIONALS.get(t, _SUFFIXES.get(t, t)) for t in _WS.sub(" ", s).split()]
    return " ".join(t for t in tokens if t).strip()


def build_address(row: dict, field: str | None, components: list[str] | None) -> str:
    """Return the raw address string for a row, from a single field or from parts."""
    if field and row.get(field):
        return str(row[field]).strip()
    if components:
        parts = [str(row.get(c, "")).strip() for c in components]
        return _WS.sub(" ", " ".join(p for p in parts if p and p.lower() != "nan")).strip()
    return ""
