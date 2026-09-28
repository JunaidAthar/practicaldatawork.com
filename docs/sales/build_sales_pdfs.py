import random, datetime as dt, asyncio, os
from playwright.async_api import async_playwright

BRAND = "Practical Data Work"
CONTACT = "Junaid Athar &nbsp;·&nbsp; practicaldatawork.com<br>junaid@practicaldatawork.com &nbsp;·&nbsp; 847-224-8510"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
os.makedirs(HERE, exist_ok=True)

CSS = """
@page { size: Letter; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Helvetica Neue', Arial, sans-serif; color: #1c2430; font-size: 10.5pt; line-height: 1.38; }
.page { width: 8.5in; height: 11in; padding: 0.5in 0.6in 0.35in; position: relative; overflow: hidden; page-break-after: always; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; }
.navy { color: #14305a; } .teal { color: #0f7c74; }
h1 { font-size: 23pt; line-height: 1.12; margin: 0 0 6px; color: #14305a; letter-spacing: -0.3px; }
h2 { font-size: 12.5pt; margin: 0 0 6px; color: #14305a; }
h3 { font-size: 10.5pt; margin: 0 0 3px; color: #14305a; }
p { margin: 0 0 6px; }
.brand { font-weight: 700; letter-spacing: 0.4px; color: #0f7c74; font-size: 10pt; text-transform: uppercase; }
.lede { font-size: 11.5pt; color: #3a4656; margin-bottom: 10px; }
.band { background: #f1f5f9; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 8px 0 2px; }
.stat { background: #fff; border-radius: 6px; padding: 8px 10px; border-left: 4px solid #0f7c74; }
.stat b { display: block; font-size: 19pt; color: #14305a; line-height: 1.05; }
.stat span { font-size: 9pt; color: #3a4656; }
.cols3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px; }
.card { border: 1px solid #d5dde6; border-radius: 8px; padding: 10px 12px; }
.card .n { font-weight: 700; color: #0f7c74; font-size: 9pt; text-transform: uppercase; letter-spacing: .4px; }
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
.step { background: #14305a; color: #fff; border-radius: 8px; padding: 9px 10px; font-size: 9.3pt; }
.step b { display: block; font-size: 10pt; margin-bottom: 2px; color: #9fe3dc; }
.two { display: grid; grid-template-columns: 1.15fr 1fr; gap: 12px; }
.price li { margin-bottom: 3px; }
ul { margin: 0; padding-left: 16px; }
.calc { border: 2px dashed #0f7c74; border-radius: 8px; padding: 10px 12px; }
.calc .line { display: flex; align-items: baseline; gap: 6px; margin: 7px 0; font-size: 10pt; flex-wrap: wrap; }
.blank { display: inline-block; border-bottom: 1.5px solid #1c2430; min-width: 58px; height: 14px; }
.small { font-size: 8pt; color: #5b6778; }
.footer { margin-top: auto; border-top: 1px solid #d5dde6; padding-top: 6px; display: flex; justify-content: space-between; font-size: 8pt; color: #5b6778; }
.cta { background: #0f7c74; color: #fff; border-radius: 8px; padding: 10px 14px; margin: 10px 0 8px; display: flex; justify-content: space-between; align-items: center; }
.cta b { font-size: 12pt; }
table { width: 100%; border-collapse: collapse; font-size: 9pt; margin-bottom: 10px; }
th { text-align: left; background: #14305a; color: #fff; padding: 5px 6px; font-weight: 600; }
td { padding: 4px 6px; border-bottom: 1px solid #e3e9ef; }
td.r, th.r { text-align: right; }
tr.tot td { font-weight: 700; background: #f1f5f9; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 10px 0 12px; }
.kpi { background: #f1f5f9; border-radius: 6px; padding: 8px 10px; }
.kpi b { display: block; font-size: 16pt; color: #14305a; }
.kpi span { font-size: 8.5pt; color: #3a4656; }
.kpi.hi { background: #0f7c74; } .kpi.hi b, .kpi.hi span { color: #fff; }
.sample { position: absolute; top: 0.22in; right: 0.6in; background: #b42318; color: #fff; font-weight: 700; font-size: 8pt; padding: 3px 8px; border-radius: 4px; letter-spacing: .5px; }
.tag { display: inline-block; padding: 1px 6px; border-radius: 10px; font-size: 8pt; font-weight: 600; }
.t-miss { background: #fde7e5; color: #b42318; } .t-340 { background: #fff1d6; color: #8a5a00; }
.t-under { background: #e6eefb; color: #14305a; } .t-late { background: #eef2f5; color: #3a4656; }
.bar { height: 10px; background: #0f7c74; border-radius: 3px; display: inline-block; vertical-align: middle; }
"""

def html(body, title):
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"

# ------------------------------------------------------------------ ONE-PAGER
onepager = f"""
<div class="page">
  <div class="brand">{BRAND}</div>
  <h1>Get every Medicare negotiated-price refund you're owed.</h1>
  <div class="lede">We match every claim to its manufacturer refund, find what's missing, late or wrongly denied, and recover it for you.
  <b>You pay nothing unless we recover money.</b></div>

  <div class="band">
    <h2>The problem independents are living with</h2>
    <p>Since January 1, 2026, every fill of a negotiated drug (Eliquis, Jardiance, Xarelto, Farxiga, Januvia, Entresto and others)
    leaves you waiting on a refund from the manufacturer, often hundreds of dollars per fill.</p>
    <div class="stats">
      <div class="stat"><b>67%</b><span>of independents wait 22+ days for refunds</span></div>
      <div class="stat"><b>78%</b><span>have trouble reconciling refunds to claims</span></div>
      <div class="stat"><b>15 more</b><span>drugs join in January 2027, incl. Ozempic &amp; Wegovy</span></div>
    </div>
    <p class="small" style="margin-top:6px">Refunds are also being wrongly denied as "340B" at pharmacies with no 340B contracts (reason code N907).</p>
  </div>

  <div class="cols3">
    <div class="card"><div class="n">Find it</div><h3>Every claim, matched</h3>
      We compare what you dispensed, what each refund should be, and what actually hit your bank.</div>
    <div class="card"><div class="n">Fix it</div><h3>We chase it for you</h3>
      We file the disputes with manufacturers and escalate to CMS, including wrongful 340B denials.</div>
    <div class="card"><div class="n">Forget it</div><h3>Nothing for you to do</h3>
      A 30-minute setup, read-only access, and a clear monthly report. We never touch your dispensing system.</div>
  </div>

  <h2>How it works</h2>
  <div class="steps">
    <div class="step"><b>1 · Setup (30 min)</b>Sign our HIPAA agreement, add us to Beacon, name us as your MTF vendor, send one export.</div>
    <div class="step"><b>2 · Free audit</b>In about 2 weeks you get a dollar figure: what's missing, late and wrongly denied.</div>
    <div class="step"><b>3 · Recovery</b>We work every open claim until it's paid or closed.</div>
    <div class="step"><b>4 · Monitoring</b>Ongoing claim-level tracking and alerts. Ready for the 2027 drugs.</div>
  </div>

  <div class="two">
    <div class="card price">
      <h2>Simple pricing</h2>
      <ul>
        <li><b>Audit:</b> free, no commitment.</li>
        <li><b>Recovery:</b> 25% of what we recover. Nothing upfront, nothing if we find nothing.</li>
        <li><b>Monitoring:</b> $199/month, month to month. Cancel anytime.</li>
        <li><b>Your data:</b> HIPAA business associate agreement signed before we see anything. Read-only access.</li>
      </ul>
    </div>
    <div class="calc">
      <h2>What's flowing through your store?</h2>
      <div class="line">Monthly fills of negotiated drugs: <span class="blank"></span></div>
      <div class="line">× average refund per fill: <b>~$375</b>*</div>
      <div class="line">= refunds owed to you each month: <b>$</b><span class="blank" style="min-width:80px"></span></div>
      <div class="line">× 12 = per year: <b>$</b><span class="blank" style="min-width:80px"></span></div>
      <div class="small">*Example: Eliquis, 60 tablets ≈ list price minus the Medicare negotiated price. Varies by drug.</div>
    </div>
  </div>

  <div class="cta"><div><b>Book your free audit</b><br>We'll show you, in dollars, what you're owed.</div><div style="text-align:right">{CONTACT}</div></div>

  <div class="footer">
    <span>Statistics: NCPA survey of independent pharmacies, Feb 2026; KFF. {BRAND} is independent and not affiliated with CMS, NCPA, Beacon, or any manufacturer.</span>
  </div>
</div>
"""

# ------------------------------------------------------------------ SAMPLE AUDIT (fictional data)
random.seed(7)
drugs = [("Eliquis", 0.38, 375), ("Jardiance", 0.18, 400), ("Xarelto", 0.13, 380),
         ("Farxiga", 0.12, 400), ("Januvia", 0.10, 415), ("Entresto", 0.09, 395)]
N = 486
start = dt.date(2026, 4, 1); end = dt.date(2026, 9, 15)
claims = []
for i in range(N):
    d = random.choices(drugs, weights=[x[1] for x in drugs])[0]
    fill = start + dt.timedelta(days=random.randint(0, (end - start).days))
    exp = round(d[2] * random.uniform(0.95, 1.05), 2)
    claims.append(dict(rx=f"RX-{700100 + i*7}", fill=fill, drug=d[0], exp=exp, paid=exp, issue="", days=None))
idx = list(range(N)); random.shuffle(idx)
miss, b340, under = idx[:9], idx[9:16], idx[16:22]
for k in miss: claims[k]["paid"] = 0; claims[k]["issue"] = "miss"
for k in b340: claims[k]["paid"] = 0; claims[k]["issue"] = "340"
for k in under:
    claims[k]["paid"] = round(claims[k]["exp"] - random.uniform(45, 130), 2); claims[k]["issue"] = "under"
for c in claims:
    if c["issue"] in ("miss", "340"): continue
    c["days"] = random.choices([random.randint(15, 21), random.randint(22, 28), random.randint(29, 45), random.randint(46, 70)],
                               weights=[30, 45, 20, 5])[0]

exp_t = sum(c["exp"] for c in claims); paid_t = sum(c["paid"] for c in claims)
gap = exp_t - paid_t
recov_rate = 0.85
fee = 0.25
def m(x): return f"${x:,.0f}"
issues = [("miss", "Missing: no refund received", "t-miss"), ("340", "Denied as 340B (no 340B contracts on file)", "t-340"),
          ("under", "Underpaid vs. expected refund", "t-under")]
iss_rows = ""
for key, label, cls in issues:
    cs = [c for c in claims if c["issue"] == key]; g = sum(c["exp"] - c["paid"] for c in cs)
    iss_rows += f"<tr><td><span class='tag {cls}'>{label}</span></td><td class='r'>{len(cs)}</td><td class='r'>{m(g)}</td></tr>"
iss_rows += f"<tr class='tot'><td>Total recoverable</td><td class='r'>{len(miss)+len(b340)+len(under)}</td><td class='r'>{m(gap)}</td></tr>"

drug_rows = ""
for d in drugs:
    cs = [c for c in claims if c["drug"] == d[0]]
    e = sum(c["exp"] for c in cs); p = sum(c["paid"] for c in cs)
    drug_rows += f"<tr><td>{d[0]}</td><td class='r'>{len(cs)}</td><td class='r'>{m(e)}</td><td class='r'>{m(p)}</td><td class='r'>{m(e-p)}</td><td class='r'>{(e-p)/e:.1%}</td></tr>"
drug_rows += f"<tr class='tot'><td>Total</td><td class='r'>{N}</td><td class='r'>{m(exp_t)}</td><td class='r'>{m(paid_t)}</td><td class='r'>{m(gap)}</td><td class='r'>{gap/exp_t:.1%}</td></tr>"

paid_claims = [c for c in claims if c["days"] is not None]
buckets = [("15–21 (target)", 15, 21), ("22–28 days", 22, 28), ("29–45 days", 29, 45), ("46+ days", 46, 999)]
bmax = max(len([c for c in paid_claims if lo <= c["days"] <= hi]) for _, lo, hi in buckets)
time_rows = ""
for lab, lo, hi in buckets:
    cs = [c for c in paid_claims if lo <= c["days"] <= hi]
    time_rows += (f"<tr><td>{lab}</td><td class='r'>{len(cs)}</td><td class='r'>{len(cs)/len(paid_claims):.0%}</td>"
                  f"<td><span class='bar' style='width:{int(170*len(cs)/bmax)}px'></span></td></tr>")
avg_days = sum(c["days"] for c in paid_claims) / len(paid_claims)
late = [c for c in paid_claims if c["days"] > 21]
float_cost = sum(c["paid"] for c in claims) / ((end - start).days) * (avg_days - 21)  # extra cash tied up

act = {"miss": "Check MTF routing; file inquiry with manufacturer", "340": "Good-faith inquiry with HRSA registry proof",
       "under": "Good-faith inquiry with wholesaler invoice"}
exc = sorted([c for c in claims if c["issue"]], key=lambda c: c["fill"])[:11]
exc_rows = ""
tagmap = {"miss": ("Missing", "t-miss"), "340": ("340B denial", "t-340"), "under": ("Underpaid", "t-under")}
for c in exc:
    t, cls = tagmap[c["issue"]]
    exc_rows += (f"<tr><td>{c['rx']}</td><td>{c['fill']:%m/%d/%Y}</td><td>{c['drug']}</td><td class='r'>{m(c['exp'])}</td>"
                 f"<td class='r'>{m(c['paid'])}</td><td><span class='tag {cls}'>{t}</span></td><td>{act[c['issue']]}</td></tr>")

recovered = gap * recov_rate
audit = f"""
<div class="page">
  <div class="sample">SAMPLE · FICTIONAL DATA</div>
  <div class="brand">{BRAND}</div>
  <h1 style="font-size:21pt">MFP Refund Audit</h1>
  <div class="lede" style="margin-bottom:6px">Main Street Pharmacy (sample) &nbsp;·&nbsp; Fills 04/01/2026 – 09/15/2026 &nbsp;·&nbsp; Prepared 10/2026</div>

  <div class="kpis">
    <div class="kpi"><b>{N}</b><span>negotiated-drug claims reviewed</span></div>
    <div class="kpi"><b>{m(exp_t)}</b><span>refunds owed to you</span></div>
    <div class="kpi"><b>{avg_days:.0f} days</b><span>average wait for refunds (target ≈ 21)</span></div>
    <div class="kpi hi"><b>{m(gap)}</b><span>missing or underpaid ({gap/exp_t:.1%})</span></div>
  </div>

  <h2>What we found</h2>
  <table><tr><th>Issue</th><th class="r">Claims</th><th class="r">Amount</th></tr>{iss_rows}</table>

  <div class="two">
    <div>
      <h2>By drug</h2>
      <table><tr><th>Drug</th><th class="r">Fills</th><th class="r">Owed</th><th class="r">Received</th><th class="r">Gap</th><th class="r">Gap %</th></tr>{drug_rows}</table>
    </div>
    <div>
      <h2>How long refunds took</h2>
      <table><tr><th>Days to refund</th><th class="r">Claims</th><th class="r">Share</th><th></th></tr>{time_rows}</table>
      <p class="small">{len(late)} of {len(paid_claims)} paid claims ({len(late)/len(paid_claims):.0%}) arrived after 21 days.
      The slower-than-target payments tie up roughly {m(float_cost)} of your cash at any given time.</p>
    </div>
  </div>

  <div class="band" style="margin-top:4px">
    <h2>What recovery would look like</h2>
    <table style="margin:0">
      <tr><td>Recoverable amount identified</td><td class="r">{m(gap)}</td></tr>
      <tr><td>Expected recovery (assumes ~{recov_rate:.0%} success)</td><td class="r">{m(recovered)}</td></tr>
      <tr><td>Our fee (25% of amount actually recovered)</td><td class="r">({m(recovered*fee)})</td></tr>
      <tr class="tot"><td>Net back to you</td><td class="r">{m(recovered*(1-fee))}</td></tr>
    </table>
  </div>
  <div class="footer"><span>{BRAND} · Sample report with fictional pharmacy, claims and amounts, for illustration only.</span><span>Page 1 of 2</span></div>
</div>

<div class="page">
  <div class="sample">SAMPLE · FICTIONAL DATA</div>
  <div class="brand">{BRAND}</div>
  <h2 style="font-size:15pt; margin-top:4px">Claim-level exceptions (first {len(exc)} of {len(miss)+len(b340)+len(under)})</h2>
  <p class="small">Full list delivered as a spreadsheet. Prescription numbers are fictional.</p>
  <table>
    <tr><th>Rx #</th><th>Fill date</th><th>Drug</th><th class="r">Expected</th><th class="r">Received</th><th>Issue</th><th>Next action</th></tr>
    {exc_rows}
  </table>

  <h2>Why these happened</h2>
  <div class="cols3">
    <div class="card"><div class="n">Missing</div>No refund line in the MTF payment files. Common causes: enrollment or bank-routing problems,
      or a claim that never reached the manufacturer. Often fixable in bulk.</div>
    <div class="card"><div class="n">340B denials</div>Refunds denied as 340B (code N907), but HRSA's 340B registry shows no contract-pharmacy
      relationships for this store. These should be overturned.</div>
    <div class="card"><div class="n">Underpaid</div>The refund was calculated from a lower price than you actually paid.
      Your wholesaler invoices support the difference.</div>
  </div>

  <h2>Recommended next steps</h2>
  <ul style="margin-bottom:10px">
    <li><b>This week:</b> confirm MTF bank and payment-file routing (likely fixes several missing refunds at once).</li>
    <li><b>Next 2 weeks:</b> we file good-faith inquiries on all {len(b340)} 340B denials and {len(under)} underpayments.</li>
    <li><b>30 days:</b> escalate anything unresolved through the CMS MTF complaint process.</li>
    <li><b>Before January:</b> set up monitoring for the 15 drugs joining in 2027, including Ozempic and Wegovy.</li>
  </ul>

  <h2>How we did this</h2>
  <p>We matched your dispensing records to the MTF payment files, Beacon reports and bank deposits, claim by claim. Expected refunds
  were calculated from published list prices and CMS negotiated prices, and 340B status was checked against HRSA's public 340B registry (OPAIS).
  All data was handled under a signed HIPAA business associate agreement with read-only access.</p>

  <div class="cta"><div><b>Ready to recover {m(gap)}?</b><br>No upfront cost. You only pay 25% of what we actually recover.</div><div style="text-align:right">{CONTACT}</div></div>
  <div class="footer"><span>{BRAND} · Sample report with fictional pharmacy, claims and amounts, for illustration only.</span><span>Page 2 of 2</span></div>
</div>
"""

files = {"Pharmacy_One_Pager": html(onepager, "Pharmacy One-Pager"),
         "Sample_MFP_Refund_Audit": html(audit, "Sample MFP Refund Audit")}

async def render():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        for name, h in files.items():
            src = os.path.join(HERE, name + ".html"); open(src, "w").write(h)
            await pg.goto("file://" + src)
            await pg.pdf(path=f"{OUT}/{name}.pdf", format="Letter", print_background=True,
                         margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            await pg.set_viewport_size({"width": 816, "height": 1056})
            await pg.screenshot(path=os.path.join(HERE, name + ".png"), full_page=True)
        await b.close()
asyncio.run(render())
print(f"gap={gap:.0f} exp={exp_t:.0f} pct={gap/exp_t:.3%} avgdays={avg_days:.1f} float={float_cost:.0f}")
