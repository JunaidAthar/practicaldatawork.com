"""Normalize each source to a common signal table, then aggregate to one row per
property (keyed on a normalized address)."""
from __future__ import annotations

import pandas as pd

from .addressing import build_address, normalize_address


def _to_long(name: str, src: dict, df: pd.DataFrame) -> pd.DataFrame:
    """One source -> rows of (norm_address, raw_address, signal, event_date, lat, lon, owner_out_of_state)."""
    if df.empty:
        return pd.DataFrame()

    field = src.get("address_field")
    components = src.get("address_components")
    date_field = src.get("date_field")
    owner_state_field = src.get("owner_state_field")

    raw = df.apply(lambda r: build_address(r.to_dict(), field, components), axis=1)
    out = pd.DataFrame({
        "raw_address": raw,
        "norm_address": raw.map(normalize_address),
        "signal": src["signal"],
        "event_date": pd.to_datetime(df[date_field], errors="coerce") if date_field in df else pd.NaT,
        "latitude": pd.to_numeric(df.get("latitude"), errors="coerce"),
        "longitude": pd.to_numeric(df.get("longitude"), errors="coerce"),
    })
    if owner_state_field and owner_state_field in df:
        state = df[owner_state_field].astype(str).str.strip().str.upper()
        out["owner_out_of_state"] = ((state != "IL") & (state != "") & (state != "NAN")).astype(int)
    else:
        out["owner_out_of_state"] = 0

    return out[out["norm_address"] != ""]


def to_features(config: dict, frames: dict) -> pd.DataFrame:
    """Combine all sources into one row per property with signal counts/flags."""
    longs = [_to_long(n, config["sources"][n], df) for n, df in frames.items()]
    longs = [l for l in longs if not l.empty]
    if not longs:
        return pd.DataFrame()
    events = pd.concat(longs, ignore_index=True)

    grp = events.groupby("norm_address")
    features = pd.DataFrame({
        "open_violation_count": grp.apply(lambda g: int((g["signal"] == "open_violation").sum())),
        "vacancy_flag": grp.apply(lambda g: int((g["signal"] == "vacancy").any())),
        "demolition_flag": grp.apply(lambda g: int((g["signal"] == "demolition_permit").any())),
        "owner_out_of_state": grp["owner_out_of_state"].max(),
        "latest_signal_date": grp["event_date"].max(),
        "latitude": grp["latitude"].apply(lambda s: s.dropna().iloc[0] if s.notna().any() else None),
        "longitude": grp["longitude"].apply(lambda s: s.dropna().iloc[0] if s.notna().any() else None),
        # a representative human-readable address for the property
        "address": grp["raw_address"].apply(lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
    }).reset_index()
    return features
