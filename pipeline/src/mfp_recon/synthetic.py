"""Synthetic (fake) data for development and demos. Contains NO real patient or pharmacy data.

NDCs and prices are made up; do not treat them as real drug prices.
"""
import random
from datetime import date, timedelta

import pandas as pd

FAKE_DRUGS = [  # (fake ndc, basis_per_unit, mfp_per_unit, qty)
    ("99999-0001-01", 10.10, 3.85, 60),
    ("99999-0002-01", 20.00, 6.60, 30),
    ("99999-0003-01", 19.30, 6.55, 30),
    ("99999-0004-01", 19.40, 5.95, 30),
    ("99999-0005-01", 17.70, 3.80, 30),
    ("99999-0006-01", 11.50, 4.90, 60),
]


def generate(n_claims: int = 480, seed: int = 7, start=date(2026, 4, 1), end=date(2026, 9, 15),
             pharmacy_id: str = "SYN0001"):
    rnd = random.Random(seed)
    prices = pd.DataFrame(FAKE_DRUGS, columns=["ndc", "basis_per_unit", "mfp_per_unit", "qty"])
    disp, refs = [], []
    span = (end - start).days
    for i in range(n_claims):
        ndc, basis, mfp, qty = rnd.choice(FAKE_DRUGS)
        fill = start + timedelta(days=rnd.randint(0, span))
        rx = f"SYN{100000 + i}"
        disp.append(dict(pharmacy_id=pharmacy_id, rx_number=rx, fill_number="0", fill_date=fill, ndc=ndc, quantity=qty))
        expected = round((basis - mfp) * qty, 2)
        roll = rnd.random()
        if roll < 0.02:            # missing
            continue
        if roll < 0.035:           # wrongly denied as 340B
            refs.append(dict(pharmacy_id=pharmacy_id, rx_number=rx, fill_number="0", fill_date=fill, ndc=ndc,
                             amount_paid=0.0, paid_date=fill + timedelta(days=20), reason_code="N907"))
            continue
        paid = expected - (rnd.uniform(40, 120) if roll < 0.05 else 0)
        days = rnd.choices([rnd.randint(15, 21), rnd.randint(22, 28), rnd.randint(29, 45)], weights=[35, 45, 20])[0]
        refs.append(dict(pharmacy_id=pharmacy_id, rx_number=rx, fill_number="0", fill_date=fill, ndc=ndc,
                         amount_paid=round(paid, 2), paid_date=fill + timedelta(days=days), reason_code=""))
    return pd.DataFrame(disp), pd.DataFrame(refs), prices.drop(columns="qty")
