from enum import Enum


class Status(str, Enum):
    PAID_OK = "paid_ok"                  # paid in full within the target window
    PAID_LATE = "paid_late"              # paid in full, but after the target window
    UNDERPAID = "underpaid"              # paid less than expected (beyond tolerance)
    MISSING = "missing"                  # no refund line at all, and past the target window
    PENDING = "pending"                  # no refund yet, still inside the target window
    DENIED_340B_DISPUTE = "denied_340b_dispute"  # denied as 340B but store has no 340B contracts
    DENIED_340B = "denied_340b"          # denied as 340B and store IS a contract pharmacy (verify with TPA)
    DENIED_OTHER = "denied_other"        # $0 refund with another reason code
    NO_PRICE = "no_price"                # NDC missing from the price table


RECOVERABLE = {Status.UNDERPAID, Status.MISSING, Status.DENIED_340B_DISPUTE}

# Remittance Advice Remark Code used when a claim is identified as 340B (per NCPA guidance).
RARC_340B = "N907"

CLAIM_KEY = ["pharmacy_id", "rx_number", "fill_number", "fill_date", "ndc"]
