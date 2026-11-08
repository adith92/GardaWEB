import test from 'node:test';
import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import { parseCameraKey, encryptSource, decryptSource, constantTimeTokenMatch, assertRtspUrl } from '../src/security.mjs';

test('AES-256-GCM round-trip and ciphertext tamper rejection', () => {
  const key = randomBytes(32);
  const source = 'rtsp://user:pass@192.168.1.21:554/video';
  const ciphertext = encryptSource(source, key);
  assert.ok(!ciphertext.includes(source));
  assert.equal(decryptSource(ciphertext, key), source);
  const parts = ciphertext.split('.');
  parts[2] = Buffer.from('modified').toString('base64url');
  assert.throws(() => decryptSource(parts.join('.'), key));
});
test('bootstrap secrets are strictly validated', () => {
  assert.throws(() => parseCameraKey('not-a-hex-key'));
  assert.equal(parseCameraKey('a'.repeat(64)).length, 32);
  assert.equal(constantTimeTokenMatch('Bearer ' + 'a'.repeat(32), 'a'.repeat(32)), true);
  assert.equal(constantTimeTokenMatch('Bearer a', 'a'.repeat(32)), false);
});
test('camera source accepts RTSP and rejects HTTP/loopback', () => {
  assert.equal(assertRtspUrl('rtsp://192.168.1.21:554/video'), 'rtsp://192.168.1.21:554/video');
  assert.throws(() => assertRtspUrl('https://example.com/'));
  assert.throws(() => assertRtspUrl('rtsp://localhost:554/video'));
});
