import { Pool } from 'pg';
import { createApp, reconcileCameras } from './app.mjs';
import { createMediaClient } from './media.mjs';
import { parseCameraKey } from './security.mjs';

for (const name of ['DATABASE_URL', 'GARDA_ADMIN_TOKEN', 'GARDA_CAMERA_KEY_HEX', 'MEDIAMTX_API_PASSWORD']) {
  if (!process.env[name]) throw new Error('Missing environment variable: ' + name);
}
const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 6, connectionTimeoutMillis: 5000 });
const key = parseCameraKey(process.env.GARDA_CAMERA_KEY_HEX);
const media = createMediaClient(
  process.env.MEDIAMTX_API_URL || 'http://mediamtx:9997', 'garda_api', process.env.MEDIAMTX_API_PASSWORD
);
const app = await createApp({ pool, media, key, adminToken: process.env.GARDA_ADMIN_TOKEN, logger: true });
await pool.query('SELECT 1');
await app.listen({ host: '0.0.0.0', port: Number(process.env.PORT || 8088) });
const sync = () => reconcileCameras(pool, media, key, app.log).catch(() => app.log.warn('Media reconciliation deferred'));
void sync();
const timer = setInterval(sync, 30000);
async function close() { clearInterval(timer); await app.close(); await pool.end(); }
process.once('SIGTERM', () => void close());
process.once('SIGINT', () => void close());
