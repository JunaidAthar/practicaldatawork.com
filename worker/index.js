/**
 * Worker entry for practicaldatawork.com (TallyRx).
 *
 * The site deploys as a Cloudflare Worker with static assets (wrangler.toml [assets]),
 * so Pages Functions in functions/ do not run on their own. This entry routes the API
 * endpoints to those same handlers and serves everything else from static assets.
 * Internal files are excluded from assets by .assetsignore.
 */
import { onRequestPost as auditRequest } from '../functions/api/audit-request.js';
import { onRequestGet as contactsList, onRequestOptions as contactsOptions } from '../functions/api/contacts-list.js';

const notAllowed = () => new Response('Method not allowed', { status: 405, headers: { Allow: 'POST' } });

export default {
  async fetch(request, env, ctx) {
    const { pathname } = new URL(request.url);
    const ctxt = { request, env, waitUntil: ctx.waitUntil.bind(ctx) };

    if (pathname === '/api/audit-request') {
      return request.method === 'POST' ? auditRequest(ctxt) : notAllowed();
    }
    if (pathname === '/api/contacts-list') {
      if (request.method === 'GET') return contactsList(ctxt);
      if (request.method === 'OPTIONS') return contactsOptions(ctxt);
      return notAllowed();
    }
    if (pathname.startsWith('/api/')) return new Response('Not found', { status: 404 });

    return env.ASSETS.fetch(request);
  },
};
