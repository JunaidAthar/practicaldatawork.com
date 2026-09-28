/**
 * Blocks internal files and folders from being served by Cloudflare Pages.
 * Pages serves everything in the project root, so product code (pipeline/),
 * internal docs (docs/) and config files must be filtered here.
 */
const BLOCKED_PREFIXES = [
  '/pipeline', '/docs', '/functions', '/node_modules', '/marketing',
  '/chicago-deal-engine', '/.', '/admin/README',
];
const BLOCKED_EXT = /\.(md|toml|sql|py|pyc|lock|sh|txt\.bak)$/i;
const ALLOWED = new Set(['/robots.txt']);

export async function onRequest(context) {
  const path = new URL(context.request.url).pathname;
  const lower = path.toLowerCase();
  if (!ALLOWED.has(lower) && !lower.startsWith('/.well-known/') &&
      (BLOCKED_PREFIXES.some((p) => lower.startsWith(p)) || BLOCKED_EXT.test(lower))) {
    return new Response('Not found', { status: 404, headers: { 'Content-Type': 'text/plain' } });
  }
  return context.next();
}
