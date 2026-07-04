# Chicago Deal Engine

A motivated-seller **sourcing and scoring pipeline** for Chicago / Cook County real
estate, built entirely on **public open data**. It pulls distress signals from the
City of Chicago open-data portal, joins them by address, scores each property's
motivated-seller propensity 0–100, and outputs a ranked lead list ready for skip
tracing and outreach.

> **The thesis:** in rehab you make your money when you *buy*. Most local investors
> source deals by hand and overpay. This gives you an institutional-grade, compounding
> sourcing edge off data anyone can legally access — but almost nobody engineers.

## What it does

```
City/County open data  ──▶  normalize + join on address  ──▶  distress score  ──▶  ranked leads.csv
 (violations, vacancy,                                          (0–100)            + top short-list
  demolition permits)
```

Signals in v1 (all live, verified, no auth required):

| Signal | Source (City of Chicago) | Why it means "motivated" |
|---|---|---|
| Open building violations | Building Violations `22u3-xenr` | Deferred maintenance / code pressure |
| Vacant / abandoned | 311 Service Requests `v6vf-nfxy` | Vacancy is the #1 distress predictor |
| Demolition/wrecking permit | Building Permits `ydr8-5enu` | Owner has given up on the structure |
| Out-of-state owner (hint) | permit contact state | Weak absentee-owner signal |

Properties that stack multiple signals (e.g. *vacant + violations + demo permit*) rise
to the top — those are your drive-by-and-skip-trace priorities.

## Quickstart

```bash
cd chicago-deal-engine
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env         # optional: add a free Socrata app token for higher rate limits

python run.py --validate     # confirm all sources respond
python run.py --limit 6000   # fast sample run (caps rows per source)
python run.py                # full run (last 2 years, all of Chicago)
```

Outputs land in `data/processed/`:
- `chicago_leads_ranked.csv` — every scored property
- `chicago_leads_top.csv` — the top 200 short-list (set in `config.yaml`)

Each row includes `address`, `motivated_seller_score`, a plain-English `signals`
breakdown, a `suggested_action`, and `latitude`/`longitude` for mapping and skip trace.

## Configuration

Everything tunable lives in [`config.yaml`](config.yaml):
- **`fetch.lookback_days`** — how far back to pull signals (default 730).
- **`scoring.weights`** — the propensity model. Bump `vacancy`/`demolition_permit`
  if you favor deep-distress; raise `open_violation_each` for maintenance-tired owners.
- **`buy_box`** — `min_signals`, `min_score`, and `top_n` to trim the list to what you
  can actually work.

## How the score works

```
score = min(open_violations × 9, cap 45)
      + 30 if vacant/abandoned
      + 22 if demolition permit
      +  6 if out-of-state owner (hint)
      + 10 if latest signal within 365 days      → clipped to 100
```

Simple and transparent on purpose — you can defend every number to a lender or partner,
and tune it as you learn which signals convert in your submarkets.

## Roadmap (where the real alpha is)

1. **Cook County enrichment** *(scaffolded, disabled by default)* — add owner name,
   **mailing address** (true absentee detection, not just a permit hint), assessed
   value, and **last sale date** (tenure + equity) from the Cook County Assessor, plus
   **tax-delinquency** from the Treasurer. Browse <https://datacatalog.cookcountyil.gov>,
   open a dataset's **API** tab, copy the `4x4` id into `enrichment` in `config.yaml`,
   and set `enabled: true`. This is the single biggest accuracy upgrade.
2. **PIN-based join** — Cook County's real parcel key is the PIN; joining on PIN beats
   address matching. Add it during enrichment.
3. **Skip trace** — feed the top short-list to BatchSkipTracing / IDI to append owner
   phone + mailing address.
4. **Underwriting** — auto-ARV from comps + vision-AI rehab estimate from listing photos
   → filter to your buy-box's spread.
5. **Outreach + CRM** — push priority leads into a mail/SMS sequence and a CRM; track
   lead→contract→close.

## ⚖️ Legal & compliance — read this

- **Data:** every source here is public open data. This tool deliberately uses **no**
  employer, client, or otherwise-confidential data. Keep it that way.
- **Outreach is the regulated part, not the sourcing.** Any calling/texting/mailing is
  subject to **TCPA, CAN-SPAM, and Do-Not-Call**. Scrub against the DNC registry, honor
  opt-outs, and consider getting outreach templates reviewed before you send at volume.
- **Don't commit derived data.** `data/` and `*.csv` are git-ignored — lead lists and
  scraped records stay off the repo.
- Estimates and scores are decision *support*, not guarantees. Verify on the ground.
