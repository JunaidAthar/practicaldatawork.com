import argparse
from pathlib import Path

import pandas as pd

from . import opais, synthetic
from .reconcile import reconcile, summarize


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mfp-recon", description="MFP refund reconciliation")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("synth", help="write synthetic demo inputs")
    s.add_argument("--out", default="data/synthetic")

    r = sub.add_parser("reconcile", help="reconcile dispenses vs refunds")
    r.add_argument("--dispenses", required=True)
    r.add_argument("--refunds", required=True)
    r.add_argument("--prices", required=True)
    r.add_argument("--as-of", required=True)
    r.add_argument("--contract-pharmacy", action="store_true", help="store has active 340B contracts")
    r.add_argument("--out", default="out")

    o = sub.add_parser("opais-check", help="is a pharmacy listed as a 340B contract pharmacy?")
    o.add_argument("--export", required=True, help="OPAIS contract pharmacy export (.xlsx)")
    o.add_argument("--name", required=True)
    o.add_argument("--zip")

    a = ap.parse_args(argv)
    if a.cmd == "synth":
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        d, rf, p = synthetic.generate()
        d.to_csv(out / "dispenses.csv", index=False); rf.to_csv(out / "refunds.csv", index=False); p.to_csv(out / "prices.csv", index=False)
        print(f"wrote synthetic data to {out}/")
    elif a.cmd == "reconcile":
        res = reconcile(pd.read_csv(a.dispenses, dtype=str).astype({"quantity": float}),
                        pd.read_csv(a.refunds, dtype=str).astype({"amount_paid": float}),
                        pd.read_csv(a.prices).astype({"ndc": str}), a.as_of, a.contract_pharmacy)
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        res.to_csv(out / "claims.csv", index=False)
        summ = summarize(res); summ.to_csv(out / "summary.csv", index=False)
        print(summ.to_string(index=False))
        print(f"\nrecoverable total: ${res['recoverable_amount'].sum():,.2f}  ->  {out}/claims.csv")
    elif a.cmd == "opais-check":
        cp = opais.load_contract_pharmacies(a.export)
        hits = opais.find_pharmacy(cp, a.name, a.zip)
        print(f"{len(hits)} contract rows match '{a.name}'" + (f" in {a.zip}" if a.zip else ""))
        if len(hits):
            print(hits[["pharmacy_name", "pharmacy_city", "pharmacy_state", "entity_name", "contract_term"]].head(20).to_string(index=False))
        print("active 340B contracts:", opais.has_active_contracts(cp, a.name, a.zip))
        print("Note: only as complete as the export. Use a full, unfiltered export for real checks.")


if __name__ == "__main__":
    main()
