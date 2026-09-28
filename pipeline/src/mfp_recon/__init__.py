"""MFP refund reconciliation engine.

Canonical inputs (CSV, one row per record):
  dispenses.csv  pharmacy_id, rx_number, fill_number, fill_date, ndc, quantity
  refunds.csv    pharmacy_id, rx_number, fill_number, fill_date, ndc, amount_paid, paid_date, reason_code
  prices.csv     ndc, basis_per_unit, mfp_per_unit   (basis = WAC or contract price)

Source adapters (MTF 835 remittance, Beacon reports, pharmacy-system exports) convert raw files
into these canonical tables. See pipeline/README.md.
"""
__version__ = "0.1.0"
