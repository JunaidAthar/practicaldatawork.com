"""Turn per-property distress features into a 0–100 motivated-seller score plus a
human-readable rationale and a suggested next action."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd


def _signals_text(row) -> str:
    bits = []
    if row["open_violation_count"] > 0:
        bits.append(f"{int(row['open_violation_count'])} open violation(s)")
    if row["vacancy_flag"]:
        bits.append("vacant/abandoned")
    if row["demolition_flag"]:
        bits.append("demolition permit")
    if row.get("owner_out_of_state"):
        bits.append("out-of-state owner (hint)")
    return "; ".join(bits) or "—"


def _action(row) -> str:
    if row["vacancy_flag"] or row["demolition_flag"]:
        return "Priority: drive-by + skip trace"
    if row["open_violation_count"] >= 3:
        return "Skip trace + direct mail"
    if row["open_violation_count"] >= 1:
        return "Add to mail sequence"
    return "Monitor"


def score(features: pd.DataFrame, config: dict) -> pd.DataFrame:
    if features.empty:
        return features
    w = config["scoring"]["weights"]
    rec = config["scoring"]["recency"]
    max_score = config["scoring"]["max_score"]

    f = features.copy()
    viol_pts = (f["open_violation_count"] * w["open_violation_each"]).clip(upper=w["open_violation_cap"])
    s = (
        viol_pts
        + f["vacancy_flag"] * w["vacancy"]
        + f["demolition_flag"] * w["demolition_permit"]
        + f["owner_out_of_state"] * w["out_of_state_owner_hint"]
    )

    cutoff = pd.Timestamp(datetime.utcnow() - timedelta(days=rec["window_days"]))
    recent = pd.to_datetime(f["latest_signal_date"], errors="coerce") >= cutoff
    s = s + recent.astype(int) * rec["bonus"]

    f["motivated_seller_score"] = s.clip(upper=max_score).round().astype(int)
    f["signals"] = f.apply(_signals_text, axis=1)
    f["suggested_action"] = f.apply(_action, axis=1)
    f["signal_count"] = (
        (f["open_violation_count"] > 0).astype(int)
        + f["vacancy_flag"] + f["demolition_flag"]
    )
    return f


def apply_buy_box(scored: pd.DataFrame, config: dict) -> pd.DataFrame:
    bb = config["buy_box"]
    out = scored[
        (scored["signal_count"] >= bb["min_signals"])
        & (scored["motivated_seller_score"] >= bb["min_score"])
    ].copy()
    out = out.sort_values("motivated_seller_score", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    cols = [
        "rank", "motivated_seller_score", "address", "signals", "suggested_action",
        "open_violation_count", "vacancy_flag", "demolition_flag", "owner_out_of_state",
        "latest_signal_date", "latitude", "longitude", "norm_address",
    ]
    return out[[c for c in cols if c in out.columns]]
