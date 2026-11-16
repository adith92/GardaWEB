const { app, BrowserWindow, ipcMain, session, Menu } = require('electron');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { workspaceUrl, sameOrigin } = require('./policy.cjs');
let window;
let origin = '';
const setupPage = pathToFileURL(path.join(__dirname, 'connect.html')).href;
const settingsPath = () => path.join(app.getPath('userData'), 'server.json');
function connect(raw) {
  const target = workspaceUrl(raw);
  origin = target;
  fs.writeFileSync(settingsPath(), JSON.stringify({ url: target }), { mode: 0o600 });
  return window.loadURL(target).catch(() => { origin = ''; return window.loadFile('connect.html'); });
}
app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((_contents, _permission, callback) => callback(false));
  session.defaultSession.setPermissionCheckHandler(() => false);
  window = new BrowserWindow({ width: 1440, height: 950, minWidth: 800, minHeight: 600,
    title: 'GARDA Workspace', backgroundColor: '#f4f6f8',
    webPreferences: { preload: path.join(__dirname, 'preload.cjs'), contextIsolation: true,
      nodeIntegration: false, sandbox: true, webSecurity: true } });
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  window.webContents.on('will-navigate', (event, target) => {
    if (!origin || !sameOrigin(target, origin)) event.preventDefault();
  });
  window.webContents.on('will-attach-webview', event => event.preventDefault());
  Menu.setApplicationMenu(Menu.buildFromTemplate([{ label: 'GARDA', submenu: [
    { label: 'Pilih server', click: () => { origin = ''; void window.loadFile('connect.html'); } },
    { role: 'reload' }, { role: 'quit' }
  ] }]));
  ipcMain.handle('garda-connect', (event, raw) => {
    if (event.senderFrame.url !== setupPage || typeof raw !== 'string' || raw.length > 2048) {
      throw new Error('Permintaan server ditolak');
    }
    workspaceUrl(raw);
    void connect(raw);
    return { connecting: true };
  });
  let saved = '';
  try { saved = JSON.parse(fs.readFileSync(settingsPath(), 'utf8')).url; } catch {}
  const supplied = process.env.GARDA_WEB_URL || saved;
  if (supplied) { try { void connect(supplied); } catch { void window.loadFile('connect.html'); } }
  else void window.loadFile('connect.html');
});
app.on('window-all-closed', () => app.quit());
