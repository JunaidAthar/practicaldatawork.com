import pandas as pd

from mfp_recon.reconcile import reconcile, summarize
from mfp_recon import synthetic

PRICES = pd.DataFrame([{"ndc": "99999-0001-01", "basis_per_unit": 10.0, "mfp_per_unit": 4.0}])


def _d(rx, fill):
    return {"pharmacy_id": "P1", "rx_number": rx, "fill_number": "0", "fill_date": fill, "ndc": "99999-0001-01", "quantity": 60}


def _r(rx, fill, amt, paid, code=""):
    return {"pharmacy_id": "P1", "rx_number": rx, "fill_number": "0", "fill_date": fill, "ndc": "99999-0001-01",
            "amount_paid": amt, "paid_date": paid, "reason_code": code}


def run(contract=False):
    disp = pd.DataFrame([_d("ok", "2026-06-01"), _d("late", "2026-06-01"), _d("under", "2026-06-01"),
                         _d("miss", "2026-06-01"), _d("pend", "2026-09-20"), _d("n907", "2026-06-01"),
                         _d("split", "2026-06-01")])
    refs = pd.DataFrame([_r("ok", "2026-06-01", 360, "2026-06-18"), _r("late", "2026-06-01", 360, "2026-07-10"),
                         _r("under", "2026-06-01", 300, "2026-06-18"), _r("n907", "2026-06-01", 0, "2026-06-18", "N907"),
                         _r("split", "2026-06-01", 200, "2026-06-15"), _r("split", "2026-06-01", 160, "2026-06-20")])
    return reconcile(disp, refs, PRICES, as_of="2026-09-28", is_340b_contract_pharmacy=contract).set_index("rx_number")


def test_expected_refund():
    assert run().loc["ok", "expected_refund"] == 360.0  # (10 - 4) * 60


def test_classification():
    s = run()["status"]
    assert s["ok"] == "paid_ok"
    assert s["late"] == "paid_late"
    assert s["under"] == "underpaid"
    assert s["miss"] == "missing"
    assert s["pend"] == "pending"
    assert s["n907"] == "denied_340b_dispute"
    assert s["split"] == "paid_ok"  # adjustment lines are summed


def test_340b_contract_pharmacy_not_disputed():
    res = run(contract=True)
    assert res.loc["n907", "status"] == "denied_340b"
    assert res.loc["n907", "recoverable_amount"] == 0


def test_recoverable_total():
    res = run()
    # underpaid 60 + missing 360 + wrongful 340B 360
    assert round(res["recoverable_amount"].sum(), 2) == 780.0
    assert set(summarize(res)["status"]) >= {"missing", "underpaid", "denied_340b_dispute"}


def test_synthetic_runs_end_to_end():
    d, r, p = synthetic.generate(n_claims=200)
    res = reconcile(d, r, p, as_of="2026-09-28")
    assert len(res) == 200
    assert res["status"].isin(["missing", "denied_340b_dispute", "underpaid"]).any()
