/**
 * POST /api/audit-request — free MFP refund audit requests from the landing page.
 *
 * Collects BUSINESS contact information only. No patient data (PHI) is accepted here;
 * claim files are exchanged later through HIPAA-covered channels after a BAA is signed.
 *
 * Stores the request in D1 (table `contacts`, see setup-database.sql), then tries to send
 * a notification email via MailChannels. The D1 write is the source of truth.
 */
const MAX = { name: 120, email: 160, phone: 40, pharmacy: 160, location: 120, stores: 20, role: 60, has340b: 20, fills: 20, message: 1500 };

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const clean = (v, n) => String(v ?? '').trim().slice(0, n);
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

export async function onRequestPost({ request, env }) {
  let raw;
  try {
    const type = request.headers.get('Content-Type') || '';
    raw = type.includes('application/json') ? await request.json() : Object.fromEntries(await request.formData());
  } catch {
    return json({ error: 'Invalid request' }, 400);
  }

  // Honeypot: real people leave this empty.
  if (raw.website) return json({ ok: true });

  const d = Object.fromEntries(Object.entries(MAX).map(([k, n]) => [k, clean(raw[k], n)]));
  if (!d.name || !d.email || !d.pharmacy) return json({ error: 'Name, email and pharmacy name are required.' }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) return json({ error: 'Please enter a valid email.' }, 400);

  const ip = request.headers.get('CF-Connecting-IP') || null;
  const ua = clean(request.headers.get('User-Agent'), 300) || null;
  const now = new Date().toISOString();
  const summary = [
    `Phone: ${d.phone || '-'}`,
    `Location: ${d.location || '-'}`,
    `Role: ${d.role || '-'}`,
    `340B contracts: ${d.has340b || '-'}`,
    `Approx. monthly negotiated-drug fills: ${d.fills || '-'}`,
    `Notes: ${d.message || '-'}`,
  ].join('\n');

  let saved = false;
  if (env.DB) {
    try {
      await env.DB.prepare(
        `INSERT INTO contacts (name, email, company, service, budget, message, ip_address, user_agent, created_at, status)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')`
      ).bind(d.name, d.email, d.pharmacy, 'MFP refund audit', d.stores || null, summary, ip, ua, now).run();
      saved = true;
    } catch (e) {
      console.error('D1 insert failed', e);
    }
  }

  let emailed = false;
  try {
    const html = `<h2>New free-audit request</h2>
      <p><b>${esc(d.name)}</b> &lt;${esc(d.email)}&gt;<br>${esc(d.pharmacy)} · ${esc(d.stores || '?')} store(s)</p>
      <pre style="font-family:Arial,sans-serif">${esc(summary)}</pre>`;
    const r = await fetch('https://api.mailchannels.net/tx/v1/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        personalizations: [{ to: [{ email: env.NOTIFY_EMAIL || 'junaid@practicaldatawork.com' }] }],
        from: { email: 'noreply@practicaldatawork.com', name: 'Practical Data Work' },
        reply_to: { email: d.email, name: d.name },
        subject: `Audit request: ${d.pharmacy}`,
        content: [{ type: 'text/plain', value: `${d.name} <${d.email}>\n${d.pharmacy}\n\n${summary}` }, { type: 'text/html', value: html }],
      }),
    });
    emailed = r.ok;
  } catch (e) {
    console.error('Email failed', e);
  }

  if (!saved && !emailed) return json({ error: 'Something went wrong. Please call or email us directly.' }, 500);
  return json({ ok: true });
}
