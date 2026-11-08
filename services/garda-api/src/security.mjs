import { createCipheriv, createDecipheriv, randomBytes, timingSafeEqual } from 'node:crypto';

export function parseCameraKey(value) {
  if (typeof value !== 'string' || !/^[a-fA-F0-9]{64}$/.test(value))
    throw new Error('GARDA_CAMERA_KEY_HEX must be exactly 64 hex characters');
  return Buffer.from(value, 'hex');
}

export function encryptSource(source, key) {
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const encrypted = Buffer.concat([cipher.update(source, 'utf8'), cipher.final()]);
  return [iv, cipher.getAuthTag(), encrypted].map(x => x.toString('base64url')).join('.');
}

export function decryptSource(secret, key) {
  const parts = secret.split('.');
  if (parts.length !== 3) throw new Error('Invalid encrypted source');
  const [iv, tag, encrypted] = parts.map(x => Buffer.from(x, 'base64url'));
  const decipher = createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(encrypted), decipher.final()]).toString('utf8');
}

export function constantTimeTokenMatch(value, expected) {
  if (typeof value !== 'string' || !value.startsWith('Bearer ')) return false;
  const actual = Buffer.from(value.slice(7));
  const target = Buffer.from(expected);
  return actual.length === target.length && timingSafeEqual(actual, target);
}

export function assertRtspUrl(value) {
  if (typeof value !== 'string' || value.length < 12 || value.length > 2048)
    throw new Error('Invalid RTSP source length');
  let uri;
  try { uri = new URL(value); } catch { throw new Error('Invalid RTSP URL'); }
  if (!['rtsp:', 'rtsps:'].includes(uri.protocol) || !uri.hostname || uri.hash)
    throw new Error('RTSP URL must use rtsp or rtsps without a fragment');
  if (['localhost', '127.0.0.1', '::1'].includes(uri.hostname))
    throw new Error('Loopback camera URLs are not permitted');
  return value;
}
