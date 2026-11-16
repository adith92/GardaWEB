const { URL } = require('node:url');
function workspaceUrl(raw) {
  const u = new URL(raw.trim());
  const local = ['localhost', '127.0.0.1', '[::1]'].includes(u.hostname);
  if ((u.protocol !== 'https:' && !(u.protocol === 'http:' && local)) || u.username || u.password || u.search || u.hash) {
    throw new Error('Gunakan server HTTPS, atau HTTP localhost untuk pengujian lokal.');
  }
  return new URL('/workspace', u.origin).href;
}
function sameOrigin(target, origin) {
  try { return new URL(target).origin === new URL(origin).origin; } catch { return false; }
}
module.exports = { workspaceUrl, sameOrigin };
