from openpyxl import Workbook

from mfp_recon import opais

HDR = ["340B ID", "Participating", "Approved", "Entity Name", "Entity Sub-Division Name", "Address1", "Address2", "Address3",
       "City", "State", "Zip", "Second Zip", "Pharmacy Name", "Pharmacy Comments", "Pharmacy ID", "Address1", "Address2",
       "Address3", "City", "State", "Zip", "Second Zip", "Contract Begin Date", "Contract Approval Date", "Contract Term Date"]


def _export(tmp_path, rows):
    wb = Workbook(); ws = wb.active
    ws.append([None, None, "Contract Pharmacy List Export"]); ws.append(["Exported On:", "2026-09-28"])
    ws.append(["Exported By:", "Guest"]); ws.append(["Covered Entity Details"]); ws.append(HDR)
    for r in rows:
        ws.append(r)
    p = tmp_path / "cp.xlsx"; wb.save(p); return p


def _row(pharm, zip5, term=None):
    return ["CAH000", "True", "True", "SAMPLE HOSPITAL", None, "1 Main", None, None, "TOWN", "IL", "60000", None,
            pharm, None, "123", "2 Elm", None, None, "NAPERVILLE", "IL", zip5, None, "2025-01-01", "2025-01-01", term]


def test_active_and_terminated(tmp_path):
    p = _export(tmp_path, [_row("MAIN STREET PHARMACY", "60540"), _row("OLD TOWN DRUGS", "60187", "2025-06-30")])
    cp = opais.load_contract_pharmacies(p)
    assert len(cp) == 2
    assert opais.has_active_contracts(cp, "Main Street Pharmacy", "60540", as_of="2026-09-28")
    assert not opais.has_active_contracts(cp, "Old Town Drugs", as_of="2026-09-28")
    assert not opais.has_active_contracts(cp, "Not Listed Rx")
