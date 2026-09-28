import pandas as pd


def expected_refunds(dispenses: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """Expected refund = (basis_per_unit - mfp_per_unit) * quantity, floored at 0.

    Units matter: quantity must be in the same billing unit as the price table
    (tablets vs. mL vs. pens). Unit mismatches are a common source of wrong answers.
    """
    df = dispenses.merge(prices, on="ndc", how="left")
    df["expected_refund"] = ((df["basis_per_unit"] - df["mfp_per_unit"]) * df["quantity"]).clip(lower=0).round(2)
    return df
