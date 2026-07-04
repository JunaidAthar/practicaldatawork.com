#!/usr/bin/env python3
"""Filter ranked leads to the high-value North / Northwest / Near-West side ZIPs —
the real outliers (a distressed/absentee property in Lincoln Park or Bucktown is a
different animal than one in Englewood). Price band is intentionally NOT capped.

  python hotzones.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "data" / "processed" / "chicago_leads_ranked.csv"

# zip -> (region, neighborhood)
ZONES = {
    # North / lakefront
    "60614": ("North", "Lincoln Park"), "60657": ("North", "Lakeview"),
    "60613": ("North", "Lakeview/Uptown"), "60640": ("North", "Uptown"),
    "60618": ("North", "North Center/Roscoe Vlg"), "60625": ("North", "Lincoln Sq/Ravenswood"),
    "60660": ("North", "Edgewater"), "60659": ("North", "West Ridge"),
    # Northwest
    "60630": ("Northwest", "Jefferson Park"), "60641": ("Northwest", "Portage Park"),
    "60634": ("Northwest", "Dunning/Belmont Heights"), "60646": ("Northwest", "Sauganash/Edgebrook"),
    "60631": ("Northwest", "Edison Park/Norwood"), "60656": ("Northwest", "Norwood Park"),
    "60639": ("Northwest", "Belmont Cragin/Hermosa"),
    # Near West / West Town (incl. Wicker/Bucktown/Logan)
    "60647": ("Near-West", "Logan Sq/Bucktown/Wicker"), "60622": ("Near-West", "Wicker Pk/Ukr Vlg/West Town"),
    "60642": ("Near-West", "Noble Sq/West Town"), "60607": ("Near-West", "West Loop/Near West"),
    "60661": ("Near-West", "Fulton River/West Loop"), "60612": ("Near-West", "Near West/United Center"),
}


def main() -> None:
    d = pd.read_csv(CSV)
    d["zip"] = d["zip"].astype(str).str.split(".").str[0]
    d = d[d["zip"].isin(ZONES)].copy()
    d["region"] = d["zip"].map(lambda z: ZONES[z][0])
    d["area"] = d["zip"].map(lambda z: ZONES[z][1])
    d = d.sort_values("motivated_seller_score", ascending=False)

    print(f"\n{'='*78}\nNORTH / NORTHWEST / NEAR-WEST OUTLIERS  ({len(d):,} leads in target ZIPs)\n{'='*78}")
    print("By region (score>=60):")
    hot = d[d["motivated_seller_score"] >= 60]
    print(hot.groupby("region").agg(leads=("address", "size"),
                                    absentee=("absentee_owner", "sum"),
                                    vacant=("vacancy_flag", "sum"),
                                    demo=("demolition_flag", "sum")).to_string())

    cols = ["motivated_seller_score", "address", "area", "est_market_value",
            "owner_city", "owner_state", "years_owned", "signals"]
    for region in ["North", "Northwest", "Near-West"]:
        seg = d[(d["region"] == region) & (d["motivated_seller_score"] >= 60)]
        print(f"\n{'-'*78}\n{region.upper()}  — top {min(15, len(seg))} of {len(seg)}\n{'-'*78}")
        if seg.empty:
            print("  (none at score>=60)")
            continue
        with pd.option_context("display.max_colwidth", 30, "display.width", 220):
            print(seg.head(15)[[c for c in cols if c in seg.columns]].to_string(index=False))

    out = ROOT / "data" / "processed" / "hotzone_north_nw_nearwest.csv"
    d.to_csv(out, index=False)
    print(f"\n(full list -> {out})")


if __name__ == "__main__":
    main()
