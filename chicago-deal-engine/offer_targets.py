#!/usr/bin/env python3
"""Find properties where an all-cash offer near your budget is BOTH credible (value
is in range) AND likely to be accepted (owner shows they want out + has equity to
discount). Emits a skip-trace-ready CSV.

  python offer_targets.py                 # default budget $200k
  python offer_targets.py --budget 250000
"""
import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
RANKED = ROOT / "data" / "processed" / "chicago_leads_ranked.csv"
RAW_ADDR = ROOT / "data" / "raw" / "cook_parcel_addresses.csv"

# Owner-name markers
LENDER = ["BANK", "SAVINGS", "MORTGAGE", " FUND", "TRUSTEE", "NATIONAL ASSOC", "LOAN",
          "FEDERAL", "FANNIE", "FREDDIE", "HUD", "SECRETARY OF", "REO", "SERVICING"]
ENTITY = ["LLC", "L L C", " INC", " LP", "CORP", "HOLDING", "PROPERT", "MANAGEMENT",
          "VENTURE", "GROUP", "ENTERPRISE", "TRUST", "ASSOC", " CO ", "REALTY", "INVEST"]


def _pin_str(s):
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()


def _has(series, markers):
    up = series.fillna("").str.upper()
    return up.apply(lambda n: any(m in n for m in markers))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=200000)
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()
    b = args.budget

    d = pd.read_csv(RANKED, dtype={"pin": str})
    d["pin"] = _pin_str(d["pin"])
    d = d[d["pin"].notna() & (d["pin"] != "nan")]

    # bring in owner name + mailing address from the cached parcel file (join on PIN)
    a = pd.read_csv(RAW_ADDR, dtype=str,
                    usecols=["pin", "mail_address_name", "mail_address_full",
                             "mail_address_city_name", "mail_address_state"])
    a["pin"] = _pin_str(a["pin"])
    a = a.drop_duplicates("pin")
    d = d.merge(a, on="pin", how="left")

    d["owner"] = d["mail_address_name"].fillna(d.get("owner_name"))
    d["is_lender"] = _has(d["owner"], LENDER)
    d["is_entity"] = _has(d["owner"], ENTITY)

    val = pd.to_numeric(d.get("est_market_value"), errors="coerce")
    d["offer_to_value"] = (b / val).round(2)

    # 1) offer is credible: value roughly $175k–$333k so $200k reads as a real cash number
    credible = val.between(b * 0.85, b * 1.6)
    # 2) owner shows they want out
    wants_out = (d.get("vacancy_flag", 0) == 1) | (d.get("open_violation_count", 0) >= 3) | (d.get("demolition_flag", 0) == 1)
    # 3) disconnected + can afford to discount
    can_discount = (d.get("absentee_owner", 0) == 1) & ((d.get("high_equity", 0) == 1) | (d.get("long_tenure", 0) == 1))
    keep = credible & wants_out & can_discount & ~d["is_lender"]

    t = d[keep].copy()

    # acceptance propensity (0–100): weighted toward "will they SELL", not just distress
    v = pd.to_numeric
    prop = (
        (t.get("vacancy_flag", 0) * 25)
        + (t.get("out_of_state_owner", 0) * 20)
        + ((t.get("absentee_owner", 0) == 1) & (t.get("out_of_state_owner", 0) == 0)).astype(int) * 12
        + (t.get("long_tenure", 0) * 15)
        + (t.get("high_equity", 0) * 15)
        + (t.get("demolition_flag", 0) * 10)
        + (v(t.get("open_violation_count"), errors="coerce").fillna(0) * 3).clip(upper=15)
    )
    t["acceptance_propensity"] = prop.clip(upper=100).round().astype(int)
    t = t.sort_values(["acceptance_propensity", "motivated_seller_score"], ascending=False)

    out_cols = ["acceptance_propensity", "motivated_seller_score", "address", "zip",
                "est_market_value", "offer_to_value", "years_owned", "signals",
                "owner", "is_entity", "mail_address_full", "mail_address_city_name",
                "mail_address_state", "pin", "latitude", "longitude"]
    out_cols = [c for c in out_cols if c in t.columns]
    t2 = t[out_cols].rename(columns={"mail_address_full": "owner_mailing_address",
                                     "mail_address_city_name": "owner_city",
                                     "mail_address_state": "owner_state"})
    # empty columns for the skip-trace vendor to fill
    for c in ["owner_phone", "owner_phone_2", "owner_email"]:
        t2[c] = ""

    out_path = ROOT / "data" / "processed" / f"offer_targets_{b//1000}k.csv"
    t2.to_csv(out_path, index=False)

    print(f"\n{'='*80}\n${b:,} ALL-CASH OFFER TARGETS  —  {len(t2):,} properties")
    print("credible value band + owner-wants-out + absentee-with-equity, lenders excluded")
    print('='*80)
    show = ["acceptance_propensity", "address", "zip", "est_market_value", "offer_to_value",
            "years_owned", "owner", "owner_state", "signals"]
    with pd.option_context("display.max_colwidth", 26, "display.width", 240):
        print(t2.head(args.top)[[c for c in show if c in t2.columns]].to_string(index=False))
    print(f"\nskip-trace-ready file (owner + mailing address, blank phone/email cols) -> {out_path}")


if __name__ == "__main__":
    main()
