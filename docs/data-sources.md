# Data sources for a refund reconciliation

## Claim lifecycle (Part D, negotiated drug)
1. Day 0: pharmacy fills and bills the Part D plan; plan pays MFP + dispensing fee.
2. ≤ 7 days: plan submits the prescription drug event (PDE) to CMS.
3. CMS validates and routes via the Medicare Transaction Facilitator (MTF) to the manufacturer (often via Beacon).
4. ≤ 14 days: manufacturer decides: standard refund (basis − MFP), other amount, or $0 (e.g. 340B).
5. ≤ 5 business days: MTF Payment Module pays the pharmacy and sends an X12 835 remittance.
≈ 21 days end to end by design.

## Inputs
| Data | Holder | How we get it |
|---|---|---|
| Dispensing records (Rx #, fill date, NDC, qty) | Pharmacy system | Export/API with pharmacy authorization |
| Plan remittance | PBM / clearinghouse | Pharmacy portal or co-op reconciliation |
| MTF refund remittance (835) | CMS MTF Payment Module | Pharmacy designates us as third-party vendor at MTF enrollment |
| Beacon MFP reports (status, basis of pricing, denials) | Beacon, for manufacturers using it | Pharmacy adds us as a Beacon user |
| WAC and MFP per NDC | Medi-Span / First Databank (licensed); CMS (free) | License + CMS file |
| Wholesaler invoices / contract price | Wholesaler or co-op | Invoice export or co-op feed |
| 340B contract-pharmacy status | HRSA 340B OPAIS (public) | Full unfiltered export or state-by-state export |
| Which claims were actually 340B | 340B administrator (TPA): Macro Helix, Wellpartner, Sentry, Verity, CaptureRx, SUNRx, RxStrategies/Pillr, Walgreens… | Through the pharmacy's portal access or a scheduled feed |
| Bank deposits | Pharmacy's bank | Statement / feed, matched on 835 trace number |

## Recovery path
Good-faith inquiry (Beacon Resolution Center or manufacturer process) → MTF complaint via CMS help desk.

## References
- CMS MTF fact sheet: https://www.cms.gov/files/document/pharmacy-dispensing-entity-mtf-fact-sheet.pdf
- CMS MTF enrollment FAQs: https://www.cms.gov/files/document/april-mtf-enrollment-faqs.pdf
- Beacon MFP FAQ: https://mfp.support.beaconchannelmanagement.com/en/articles/12313677-frequently-asked-questions
- NCPA on 340B miscategorization (N907): https://ncpa.org/newsroom/qam/2026/08/27/340b-miscategorization-stealing-your-mfp-refunds
- HRSA OPAIS: https://hrsa.gov/opa/340b-opais
- USC Schaeffer on MFP effectuation: https://schaeffer.usc.edu/research/medicare-drug-prices-mfp-effectuation/
