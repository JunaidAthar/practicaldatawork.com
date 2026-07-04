#!/usr/bin/env python3
"""Turn the ranked lead list into concrete opportunity segments + target farms.

  python analyze.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "data" / "processed" / "chicago_leads_ranked.csv"


def _col(d, name, default=0):
    return d[name] if name in d.columns else pd.Series(default, index=d.index)


def main() -> None:
    if not CSV.exists():
        raise SystemExit(f"No output yet — run `python run.py` first ({CSV}).")
    d = pd.read_csv(CSV)
    n = len(d)
    absentee = _col(d, "absentee_owner").fillna(0).astype(int)
    oos = _col(d, "out_of_state_owner").fillna(0).astype(int)
    vac = _col(d, "vacancy_flag").fillna(0).astype(int)
    demo = _col(d, "demolition_flag").fillna(0).astype(int)
    viol = _col(d, "open_violation_count").fillna(0).astype(int)
    tenure = _col(d, "long_tenure").fillna(0).astype(int)
    matched = _col(d, "pin").notna().sum() if "pin" in d.columns else 0

    print(f"\n{'='*70}\nCHICAGO DEAL ENGINE — OPPORTUNITY SUMMARY\n{'='*70}")
    print(f"Total scored leads:            {n:,}")
    print(f"  matched to a parcel/owner:   {matched:,}")
    print(f"  absentee-owned:              {absentee.sum():,}  (out-of-state: {oos.sum():,})")
    print(f"  vacant/abandoned:            {vac.sum():,}")
    print(f"  demolition permit pulled:    {demo.sum():,}")
    print(f"  long-tenure owner (matched): {tenure.sum():,}")
    print(f"  score >= 80 / >= 60:         {(d['motivated_seller_score']>=80).sum():,} / "
          f"{(d['motivated_seller_score']>=60).sum():,}")

    def show(title, mask, cols, k=12):
        seg = d[mask]
        print(f"\n{'-'*70}\n{title}  ({len(seg):,} properties)\n{'-'*70}")
        if seg.empty:
            print("  (none)")
            return
        view = seg.head(k)[[c for c in cols if c in seg.columns]]
        with pd.option_context("display.max_colwidth", 30, "display.width", 200):
            print(view.to_string(index=False))

    base = ["motivated_seller_score", "address", "zip", "owner_city", "owner_state",
            "years_owned", "signals"]

    segments = {
        "seg_A_vacant_absentee": (vac == 1) & (absentee == 1),
        "seg_B_tired_landlord": (absentee == 1) & (tenure == 1) & (viol >= 3),
        "seg_C_demolition": demo == 1,
        "seg_D_out_of_state": oos == 1,
    }
    outdir = CSV.parent
    for name, mask in segments.items():
        d[mask].to_csv(outdir / f"{name}.csv", index=False)

    show("A) BEST FLIP/WHOLESALE — vacant + absentee (+ any violation)",
         segments["seg_A_vacant_absentee"], base)
    show("B) TIRED LANDLORD — absentee, long tenure, 3+ open violations",
         segments["seg_B_tired_landlord"], base)
    show("C) TEARDOWN / DEEP VALUE-ADD — demolition permit",
         segments["seg_C_demolition"], ["motivated_seller_score", "address", "zip", "owner_city", "signals"])
    print(f"\n(segment CSVs written to {outdir}/seg_*.csv — skip-trace ready)")

    # Target farms: ZIPs with the most high-distress leads -> direct-mail routes
    if "zip" in d.columns:
        hot = d[d["motivated_seller_score"] >= 60].copy()
        hot["zip"] = hot["zip"].astype(str).str.split(".").str[0]
        farms = (hot.groupby("zip")
                    .agg(leads=("address", "size"),
                         absentee=("absentee_owner", "sum") if "absentee_owner" in hot else ("address", "size"),
                         avg_score=("motivated_seller_score", "mean"))
                    .sort_values("leads", ascending=False).head(12))
        print(f"\n{'-'*70}\nD) TOP MAIL FARMS — ZIPs by count of score>=60 leads\n{'-'*70}")
        print(farms.round(1).to_string())

    print(f"\n{'='*70}\nNext: skip-trace segment A, drive-by the top 25, mail farms in D.\n{'='*70}\n")


if __name__ == "__main__":
    main()
