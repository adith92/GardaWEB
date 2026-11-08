import Fastify from 'fastify';
import helmet from '@fastify/helmet';
import { randomUUID } from 'node:crypto';
import { assertRtspUrl, constantTimeTokenMatch, decryptSource, encryptSource } from './security.mjs';

const createCameraSchema = {
  type: 'object', additionalProperties: false, required: ['name', 'rtspUrl'],
  properties: {
    name: { type: 'string', minLength: 1, maxLength: 100 },
    rtspUrl: { type: 'string', minLength: 12, maxLength: 2048 }
  }
};
const cameraParamSchema = {
  type: 'object', required: ['id'], properties: { id: { type: 'string', pattern: '^[0-9a-fA-F-]{36}$' } }
};

export async function createApp({ pool, media, key, adminToken, logger = false }) {
  if (!adminToken || adminToken.length < 32) throw new Error('Admin token must be at least 32 characters');
  const app = Fastify({ logger, bodyLimit: 8192, trustProxy: false });
  await app.register(helmet);
  app.get('/healthz', async () => ({ service: 'garda-basic-api', status: 'running' }));
  app.addHook('onRequest', async (req, reply) => {
    if (req.url === '/healthz') return;
    if (!constantTimeTokenMatch(req.headers.authorization, adminToken))
      return reply.code(401).send({ error: 'Unauthorized' });
  });
  app.get('/v1/cameras', async () => {
    const result = await pool.query(
      'SELECT id, name, media_path AS "mediaPath", created_at AS "createdAt" FROM cameras ORDER BY created_at'
    );
    return { cameras: result.rows };
  });
  app.post('/v1/cameras', { schema: { body: createCameraSchema } }, async (req, reply) => {
    let source;
    try { source = assertRtspUrl(req.body.rtspUrl); }
    catch { return reply.code(400).send({ error: 'Invalid RTSP URL' }); }
    const id = randomUUID();
    const path = 'cam-' + id.replaceAll('-', '');
    try {
      await pool.query(
        'INSERT INTO cameras (id, name, media_path, source_ciphertext) VALUES ($1,$2,$3,$4)',
        [id, req.body.name.trim(), path, encryptSource(source, key)]
      );
      try { await media.addCamera(path, source); }
      catch (error) { req.log.warn({ status: error.status }, 'Gateway provisioning deferred'); }
      await pool.query(
        'INSERT INTO audit_events (action, resource_id, details) VALUES ($1,$2,$3::jsonb)',
        ['camera.register', id, JSON.stringify({ name: req.body.name.trim() })]
      );
      return reply.code(201).send({ id, name: req.body.name.trim(), mediaPath: path, state: 'provisioning' });
    } catch (error) {
      req.log.error({ code: error.code }, 'Registration failed');
      return reply.code(500).send({ error: 'Registration failed' });
    }
  });
  app.get('/v1/cameras/:id/status', { schema: { params: cameraParamSchema } }, async (req, reply) => {
    const rows = await pool.query('SELECT media_path FROM cameras WHERE id=$1', [req.params.id]);
    if (!rows.rowCount) return reply.code(404).send({ error: 'Unknown camera' });
    try { return { cameraId: req.params.id, gateway: await media.cameraStatus(rows.rows[0].media_path) }; }
    catch (error) { return { cameraId: req.params.id, gatewayStatus: error.status || 'unavailable' }; }
  });
  app.get('/v1/cameras/:id/recordings', { schema: { params: cameraParamSchema } }, async (req, reply) => {
    const rows = await pool.query('SELECT media_path FROM cameras WHERE id=$1', [req.params.id]);
    if (!rows.rowCount) return reply.code(404).send({ error: 'Unknown camera' });
    try { return { cameraId: req.params.id, data: await media.recordings(rows.rows[0].media_path) }; }
    catch (error) {
      if (error.status === 404) return { cameraId: req.params.id, data: [] };
      return reply.code(503).send({ error: 'Recorder unavailable' });
    }
  });
  app.get('/v1/audit', async () => {
    const result = await pool.query(
      'SELECT id, action, resource_id AS "resourceId", details, created_at AS "createdAt" FROM audit_events ORDER BY id DESC LIMIT 100'
    );
    return { entries: result.rows };
  });
  return app;
}

export async function reconcileCameras(pool, media, key, log = console) {
  const result = await pool.query('SELECT media_path, source_ciphertext FROM cameras');
  let repaired = 0;
  for (const camera of result.rows) {
    try { await media.getConfig(camera.media_path); continue; }
    catch (error) {
      if (error.status !== 404) { log.warn('Gateway check deferred'); break; }
    }
    try {
      await media.addCamera(camera.media_path, decryptSource(camera.source_ciphertext, key));
      repaired++;
    } catch { log.warn('Camera restoration deferred'); }
  }
  return { repaired, total: result.rowCount };
}
