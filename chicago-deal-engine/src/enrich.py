"""Cook County Assessor enrichment.

Adds, per property:
  - PIN, owner name, mailing city/state, ZIP        (Parcel Addresses)
  - absentee_owner / out_of_state_owner flags        (mail address != property)
  - last sale date/price -> years_owned, long_tenure (Parcel Sales)

The address join is done locally on the normalized address key so it's robust to
minor formatting differences. Sales are pulled only for the highest-distress PINs
(cap in config) to keep the run fast.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .addressing import normalize_address
from .socrata import SocrataClient

_ADDR_COLS = [
    "pin", "prop_address_full", "prop_address_zipcode_1", "prop_address_state",
    "mail_address_name", "mail_address_full", "mail_address_city_name",
    "mail_address_state", "owner_address_name",
]


def _latest_year(client: SocrataClient, dataset_id: str) -> str:
    # one grouped request (a few rows) — NOT a full-table scan.
    # year is inconsistently "2026.0" / "2025"; pick max by float, keep original string.
    rows = client.query(dataset_id, **{"$select": "year", "$group": "year"})
    years = [r["year"] for r in rows if r.get("year")]
    return max(years, key=lambda y: float(y))


def fetch_parcel_addresses(cfg: dict, raw_dir: Path) -> pd.DataFrame:
    client = SocrataClient(cfg["domain"], page_size=50000)
    year = _latest_year(client, cfg["parcel_addresses_id"])
    where = f"upper(prop_address_city_name)='{cfg['city'].upper()}' AND year='{year}'"
    print(f"     parcel addresses: {cfg['city']} @ year {year}")
    rows = client.fetch_all(cfg["parcel_addresses_id"], select=_ADDR_COLS, where=where)
    df = pd.DataFrame(rows)
    raw_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(raw_dir / "cook_parcel_addresses.csv", index=False)
    return df


def _fetch_sales(cfg: dict, pins: list[str]) -> pd.DataFrame:
    """Latest sale per PIN, batched by pin IN (...)."""
    client = SocrataClient(cfg["domain"], page_size=50000)
    ds = cfg["parcel_sales_id"]
    frames = []
    for i in range(0, len(pins), 500):
        batch = [p for p in pins[i:i + 500] if p]
        if not batch:
            continue
        in_list = ",".join("'" + p.replace("'", "") + "'" for p in batch)
        rows = client.fetch_all(ds, select="pin,sale_date,sale_price",
                                where=f"pin in ({in_list})", order="pin")
        if rows:
            frames.append(pd.DataFrame(rows))
    if not frames:
        return pd.DataFrame(columns=["pin", "last_sale_date", "last_sale_price"])
    sales = pd.concat(frames, ignore_index=True)
    sales["sale_date"] = pd.to_datetime(sales["sale_date"], errors="coerce")
    sales["sale_price"] = pd.to_numeric(sales["sale_price"], errors="coerce")
    latest = (sales.sort_values("sale_date")
                    .groupby("pin", as_index=False)
                    .agg(last_sale_date=("sale_date", "last"),
                         last_sale_price=("sale_price", "last")))
    return latest


def _fetch_values(cfg: dict, pins: list[str]) -> pd.DataFrame:
    """Latest available assessed total per PIN -> assessor-implied market value.
    (2026 values aren't published yet, so we take the most recent year that has a
    non-null total.)"""
    client = SocrataClient(cfg["domain"], page_size=50000)
    ds = cfg["parcel_values_id"]
    frames = []
    for i in range(0, len(pins), 500):
        batch = [p for p in pins[i:i + 500] if p]
        if not batch:
            continue
        in_list = ",".join("'" + p.replace("'", "") + "'" for p in batch)
        rows = client.fetch_all(ds, select="pin,year,mailed_tot,certified_tot,board_tot",
                                where=f"pin in ({in_list})", order="pin")
        if rows:
            frames.append(pd.DataFrame(rows))
    if not frames:
        return pd.DataFrame(columns=["pin", "assessed_tot"])
    v = pd.concat(frames, ignore_index=True)
    for c in ["mailed_tot", "certified_tot", "board_tot"]:
        v[c] = pd.to_numeric(v.get(c), errors="coerce")
    # board (post-appeal) > certified > mailed
    v["assessed_tot"] = v["board_tot"].fillna(v["certified_tot"]).fillna(v["mailed_tot"])
    v["year_num"] = pd.to_numeric(v["year"], errors="coerce")
    v = v.dropna(subset=["assessed_tot"]).sort_values("year_num")
    latest = v.groupby("pin", as_index=False).agg(assessed_tot=("assessed_tot", "last"))
    return latest


def enrich(features: pd.DataFrame, cfg: dict, raw_dir: Path,
           prescore: pd.Series | None = None) -> pd.DataFrame:
    if features.empty:
        return features

    addr = fetch_parcel_addresses(cfg, raw_dir)
    addr["norm_address"] = addr["prop_address_full"].map(normalize_address)
    addr = addr[addr["norm_address"] != ""]
    # condos/multi-parcel share an address; flag and keep one PIN
    counts = addr.groupby("norm_address")["pin"].transform("size")
    addr["is_multiparcel"] = (counts > 1).astype(int)
    addr = addr.drop_duplicates("norm_address", keep="first")

    mail_norm = addr["mail_address_full"].map(normalize_address)
    mail_state = addr["mail_address_state"].astype(str).str.strip().str.upper()
    addr["absentee_owner"] = ((mail_norm != addr["norm_address"]) & (mail_norm != "")).astype(int)
    addr["out_of_state_owner"] = ((mail_state != "IL") & (mail_state != "") & (mail_state != "NAN")).astype(int)
    addr["owner_name"] = addr["mail_address_name"].fillna(addr["owner_address_name"])

    keep = ["norm_address", "pin", "owner_name", "mail_address_full", "mail_address_city_name",
            "mail_address_state", "prop_address_zipcode_1", "absentee_owner",
            "out_of_state_owner", "is_multiparcel"]
    out = features.merge(addr[keep], on="norm_address", how="left")
    out = out.rename(columns={"mail_address_full": "owner_mailing_address",
                              "mail_address_city_name": "owner_city",
                              "mail_address_state": "owner_state",
                              "prop_address_zipcode_1": "zip"})
    for c in ["absentee_owner", "out_of_state_owner", "is_multiparcel"]:
        out[c] = out[c].fillna(0).astype(int)

    # Sales: only for matched PINs, prioritized by distress, capped.
    matched = out[out["pin"].notna()].copy()
    if prescore is not None:
        matched = matched.assign(_p=prescore.reindex(matched.index)).sort_values("_p", ascending=False)
    pins = matched["pin"].head(cfg["sales_max_pins"]).tolist()
    print(f"     pulling sales history for {len(pins):,} PINs")
    sales = _fetch_sales(cfg, pins)

    out = out.merge(sales, on="pin", how="left")
    now = pd.Timestamp(datetime.utcnow())
    out["years_owned"] = ((now - pd.to_datetime(out["last_sale_date"], errors="coerce")).dt.days / 365.25)
    out["long_tenure"] = (out["years_owned"] >= cfg["long_tenure_years"]).fillna(False).astype(int)

    # Assessor-implied market value + equity proxy (same PIN set as sales).
    values = _fetch_values(cfg, pins)
    out = out.merge(values, on="pin", how="left")
    out["est_market_value"] = (out["assessed_tot"] * cfg["assessment_ratio"]).round(-3)
    out["equity_proxy"] = out["est_market_value"] - out["last_sale_price"]
    out["high_equity"] = (out["equity_proxy"] >= cfg["high_equity_min"]).fillna(False).astype(int)
    return out
