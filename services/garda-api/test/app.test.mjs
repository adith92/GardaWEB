import test from 'node:test';
import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import { createApp } from '../src/app.mjs';

const adminToken = 'a'.repeat(48);
const fakePool = { query: async () => ({ rows: [], rowCount: 0 }) };
const fakeMedia = {};

test('API rejects anonymous users before querying the database', async () => {
  const app = await createApp({ pool: fakePool, media: fakeMedia, key: randomBytes(32), adminToken });
  try {
    const anon = await app.inject({ method: 'GET', url: '/v1/cameras' });
    assert.equal(anon.statusCode, 401);
    const allowed = await app.inject({ method: 'GET', url: '/v1/cameras', headers: { authorization: 'Bearer ' + adminToken } });
    assert.equal(allowed.statusCode, 200);
    assert.deepEqual(allowed.json(), { cameras: [] });
    assert.equal((await app.inject({ method: 'GET', url: '/healthz' })).statusCode, 200);
  } finally { await app.close(); }
});
