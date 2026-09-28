"""Classify every dispensed MFP claim against the refunds actually received."""
import pandas as pd

from .models import CLAIM_KEY, RARC_340B, RECOVERABLE, Status
from .pricing import expected_refunds

TARGET_DAYS = 21          # ~7 days plan->CMS + 14 days manufacturer + banking (CMS average)
UNDERPAY_TOLERANCE = 1.00  # dollars


def _prep(df: pd.DataFrame, date_cols) -> pd.DataFrame:
    df = df.copy()
    for c in ["pharmacy_id", "rx_number", "fill_number", "ndc"]:
        if c in df:
            df[c] = df[c].astype(str).str.strip()
    for c in date_cols:
        if c in df:
            df[c] = pd.to_datetime(df[c])
    return df


def reconcile(dispenses: pd.DataFrame, refunds: pd.DataFrame, prices: pd.DataFrame,
              as_of, is_340b_contract_pharmacy: bool = False) -> pd.DataFrame:
    """Return one row per dispensed claim with expected vs. paid, days to pay and a Status.

    Refund lines for the same claim (e.g. an initial payment plus an adjustment) are summed.
    """
    as_of = pd.Timestamp(as_of)
    d = _prep(dispenses, ["fill_date"])
    r = _prep(refunds, ["fill_date", "paid_date"])
    r["reason_code"] = r.get("reason_code", pd.Series(dtype=str)).fillna("").astype(str).str.upper().str.strip()

    agg = (r.groupby(CLAIM_KEY, dropna=False)
             .agg(amount_paid=("amount_paid", "sum"), paid_date=("paid_date", "max"),
                  reason_codes=("reason_code", lambda s: ",".join(sorted({x for x in s if x}))),
                  refund_lines=("amount_paid", "size"))
             .reset_index())

    df = expected_refunds(d, _prep(prices, [])).merge(agg, on=CLAIM_KEY, how="left")
    df["amount_paid"] = df["amount_paid"].fillna(0.0).round(2)
    df["refund_lines"] = df["refund_lines"].fillna(0).astype(int)
    df["reason_codes"] = df["reason_codes"].fillna("")
    df["days_to_pay"] = (df["paid_date"] - df["fill_date"]).dt.days
    df["days_outstanding"] = (as_of - df["fill_date"]).dt.days
    df["gap"] = (df["expected_refund"] - df["amount_paid"]).round(2)

    def classify(row) -> str:
        if pd.isna(row["expected_refund"]):
            return Status.NO_PRICE.value
        if row["refund_lines"] == 0:
            return (Status.PENDING if row["days_outstanding"] <= TARGET_DAYS else Status.MISSING).value
        if row["amount_paid"] <= 0:
            if RARC_340B in row["reason_codes"]:
                return (Status.DENIED_340B if is_340b_contract_pharmacy else Status.DENIED_340B_DISPUTE).value
            return Status.DENIED_OTHER.value
        if row["gap"] > UNDERPAY_TOLERANCE:
            return Status.UNDERPAID.value
        return (Status.PAID_LATE if row["days_to_pay"] > TARGET_DAYS else Status.PAID_OK).value

    df["status"] = df.apply(classify, axis=1)
    df["recoverable"] = df["status"].isin({s.value for s in RECOVERABLE})
    df["recoverable_amount"] = df["gap"].where(df["recoverable"], 0.0).clip(lower=0).round(2)
    return df


def summarize(result: pd.DataFrame) -> pd.DataFrame:
    """Counts and dollars by status."""
    return (result.groupby("status")
                  .agg(claims=("status", "size"), expected=("expected_refund", "sum"),
                       paid=("amount_paid", "sum"), recoverable=("recoverable_amount", "sum"))
                  .round(2).sort_values("recoverable", ascending=False).reset_index())
