# mfp-recon — MFP refund reconciliation engine

Matches every dispensed Medicare negotiated-price (MFP) claim to the manufacturer refunds actually
received, and classifies each claim so recoverable dollars can be worked.

> **No real patient data in this repo, ever.** Develop and test on synthetic data (`mfp-recon synth`).
> Real claim files are processed only inside HIPAA-covered infrastructure (see `docs/hipaa.md`).
> `data/` and `out/` are gitignored for this reason.

## Quick start
```bash
cd pipeline
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest -q
mfp-recon synth --out data/synthetic
mfp-recon reconcile --dispenses data/synthetic/dispenses.csv --refunds data/synthetic/refunds.csv \
  --prices data/synthetic/prices.csv --as-of 2026-09-28 --out out
mfp-recon opais-check --export path/to/340B_ContractPharmacy_Export.xlsx --name "Main Street Pharmacy" --zip 60540
```

## Canonical inputs
| Table | Columns | Real source (adapter to build) |
|---|---|---|
| `dispenses` | pharmacy_id, rx_number, fill_number, fill_date, ndc, quantity | Pharmacy system export (PioneerRx, Liberty, BestRx, RedSail…) |
| `refunds` | pharmacy_id, rx_number, fill_number, fill_date, ndc, amount_paid, paid_date, reason_code | MTF X12 835 remittance + Beacon MFP reports |
| `prices` | ndc, basis_per_unit, mfp_per_unit | CMS negotiated-price file + licensed WAC (Medi-Span / First Databank) or wholesaler contract price |
| 340B status | — | HRSA OPAIS contract-pharmacy export (`opais.py`); 340B administrator (TPA) reports if the store has contracts |

## Statuses
`paid_ok`, `paid_late` (> 21 days), `underpaid`, `missing`, `pending`, `denied_340b_dispute`
(N907 at a store with no active 340B contracts), `denied_340b` (store has contracts; verify with TPA data),
`denied_other`, `no_price`. Recoverable = `underpaid` + `missing` + `denied_340b_dispute`.

## Roadmap
1. **835 adapter**: parse MTF remittance (CLP/SVC/CAS/LQ segments) into `refunds`. Confirm claim identifiers against real sample files first.
2. **Beacon report adapter**: refund status, basis of pricing, denial reasons.
3. **Pharmacy-system adapters**: one per vendor export format.
4. **Units**: normalize billing units (tablets, mL, pens) between dispenses and price table.
5. **Price table loader**: CMS MFP file + WAC by NDC and effective date.
6. **Reversals / re-bills**: net reversed claims before matching.
7. **Outputs**: good-faith-inquiry packets per manufacturer; the client audit PDF (see `docs/sales/`).
