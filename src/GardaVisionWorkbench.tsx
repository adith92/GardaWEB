import { useEffect, useState } from "react";

type Camera = { id: string; site_id: string; rtsp_configured: boolean; ptz_configured: boolean; running: boolean; last_error?: string | null };
type NetInterface = { interface: string; ip: string; network: string; suggested_cidr: string };
type PortFinding = { port: number; hint: string; evidence: string; banner?: string };
type NetDevice = { ip: string; mac?: string | null; classification: string; onvif_ws_discovery?: boolean; flags: string[]; open_ports: PortFinding[] };
type ScanState = { id: string; status: string; network: string; mode: string; target_ip?: string | null; result: { devices: NetDevice[]; host_count?: number; duration_seconds?: number; cautions?: string[]; error?: string } };
type EventRecord = { id: string; time_utc: string; site_id: string; camera_id: string; kind: string; data: Record<string, unknown> };
const API = "http://127.0.0.1:8765/api/v1";

/** Intentionally local-only LAB UI: no token persistence; never enable on public Vercel. */
export default function GardaVisionWorkbench() {
  const [token, setToken] = useState("");
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [events, setEvents] = useState<EventRecord[]>([]);
  const [selected, setSelected] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("Hubungkan service lokal. Hanya untuk pengembangan.");
  const [busy, setBusy] = useState(false);
  const [interfaces, setInterfaces] = useState<NetInterface[]>([]);
  const [scanCidr, setScanCidr] = useState("");
  const [scanMode, setScanMode] = useState<"quick" | "extended">("quick");
  const [targetIp, setTargetIp] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const [scanJob, setScanJob] = useState("");
  const [scanState, setScanState] = useState<ScanState | null>(null);

  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(API + path, {
      ...init,
      headers: { Authorization: `Bearer ${token}`, ...(init?.headers || {}) },
    });
    if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
    return res.json() as Promise<T>;
  }

  async function refresh() {
    try {
      const [cams, ev] = await Promise.all([
        request<Camera[]>("/cameras"),
        request<EventRecord[]>("/events?limit=40"),
      ]);
      setCameras(cams);
      setEvents(ev);
      setSelected((old) => old || cams[0]?.id || "");
      setMessage(`Terhubung ke GARDA Vision LAB: ${cams.length} kamera terkonfigurasi`);
    } catch (err) { setMessage(String(err)); }
  }

  async function loadInterfaces() {
    try {
      const list = await request<NetInterface[]>("/network/interfaces");
      setInterfaces(list);
      setScanCidr((old) => old || list[0]?.suggested_cidr || "");
      if (!list.length) setMessage("Tidak menemukan interface IPv4 privat aktif di komputer backend.");
    } catch (err) { setMessage(`Network discovery hanya untuk admin: ${String(err)}`); }
  }

  async function startScan() {
    if (!authorized || !scanCidr || !token) return;
    setBusy(true);
    try {
      const job = await request<{ scan_id: string; status: string }>("/network/scans", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cidr: scanCidr, mode: scanMode, target_ip: targetIp.trim() || null, confirm_authorized: true }),
      });
      setScanJob(job.scan_id);
      setScanState(null);
      setMessage(`Scan dimulai, ID: ${job.scan_id}. Hasil hanya disimpan lokal.`);
    } catch (err) { setMessage(String(err)); }
    finally { setBusy(false); }
  }

  useEffect(() => {
    if (!token || !scanJob) return;
    let stopped = false;
    async function poll() {
      try {
        const res = await fetch(`${API}/network/scans/${encodeURIComponent(scanJob)}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = (await res.json()) as ScanState;
        if (!stopped) setScanState(data);
      } catch (err) { if (!stopped) setMessage(`Status scan gagal dibaca: ${String(err)}`); }
    }
    void poll();
    const interval = window.setInterval(() => { void poll(); }, 1200);
    return () => { stopped = true; window.clearInterval(interval); };
  }, [token, scanJob]);

  async function act(path: string, body?: object) {
    setBusy(true);
    try {
      const res = await request<Record<string, unknown>>(path, { method: "POST", ...(body ? { headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {}) });
      setMessage(JSON.stringify(res));
      await refresh();
    } catch (err) { setMessage(String(err)); }
    finally { setBusy(false); }
  }

  async function analyze() {
    if (!selected || !file) return;
    const form = new FormData();
    form.append("image", file);
    setBusy(true);
    try {
      const result = await request<Record<string, unknown>>(`/cameras/${encodeURIComponent(selected)}/analyze`, { method: "POST", body: form });
      setMessage(JSON.stringify(result, null, 2));
      await refresh();
    } catch (err) { setMessage(String(err)); }
    finally { setBusy(false); }
  }

  // No polling without a token; no secret in storage, query strings or build variables.
  useEffect(() => { setCameras([]); setEvents([]); setInterfaces([]); setScanState(null); setScanJob(""); setAuthorized(false); }, [token]);

  return (
    <section style={{ padding: 24, color: "#20242d", maxWidth: 1150, margin: "0 auto" }}>
      <h1>GARDA AI Vision | Development Lab</h1>
      <p>Windows / Linux · Backend terpisah · Semua hasil ANPR/wajah adalah kandidat yang perlu verifikasi manusia. Tidak menggunakan data demo GARDAWEB.</p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, margin: "16px 0" }}>
        <input aria-label="Local operator bearer token" type="password" placeholder="Token operator/admin lokal" value={token} onChange={(e) => setToken(e.target.value)} style={{ width: 310 }} />
        <button disabled={!token} onClick={() => { void refresh(); void loadInterfaces(); }}>Hubungkan & perbarui</button>
        <select aria-label="Pilih kamera" value={selected} onChange={(e) => setSelected(e.target.value)}>
          {cameras.map((camera) => <option key={camera.id} value={camera.id}>{camera.id} ({camera.site_id})</option>)}
        </select>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 20 }}>
        <button disabled={busy || !selected} onClick={() => act(`/cameras/${encodeURIComponent(selected)}/start`)}>Start AI inference</button>
        <button disabled={busy || !selected} onClick={() => act(`/cameras/${encodeURIComponent(selected)}/stop`)}>Stop AI inference</button>
        <button disabled={busy || !selected} onClick={() => act(`/cameras/${encodeURIComponent(selected)}/zoom`, { speed: 0.5, seconds: 0.4 })}>Zoom + (optical PTZ)</button>
        <button disabled={busy || !selected} onClick={() => act(`/cameras/${encodeURIComponent(selected)}/zoom`, { speed: -0.5, seconds: 0.4 })}>Zoom - (optical PTZ)</button>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 14 }}>
        <input aria-label="JPEG atau PNG untuk analisis" type="file" accept="image/png,image/jpeg" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button disabled={busy || !file || !selected} onClick={analyze}>Analisis foto kamera</button>
      </div>
      <pre style={{ whiteSpace: "pre-wrap", background: "#f2f4f6", padding: 12, borderRadius: 8 }}>{message}</pre>
      <section aria-label="GARDA LAN Scanner" style={{ border: "1px solid #d7dce4", borderRadius: 10, background: "#fff", padding: 16, marginBottom: 24 }}>
        <h2>LAN Discovery & CCTV Port Scanner <small style={{ color: "#777" }}>Windows / Linux, mandiri</small></h2>
        <p>Memindai interface privat yang dipilih dari komputer backend. Admin saja; tidak mencoba login Telnet/FTP, mengubah CCTV, atau memindai internet. Port terbuka bukan bukti kemampuan ONVIF/RTSP.</p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, alignItems: "end" }}>
          <label>Subnet privat<br />
            <select aria-label="Subnet LAN" value={scanCidr} onChange={e => setScanCidr(e.target.value)}>
              {!interfaces.length && <option value="">Klik Hubungkan untuk deteksi interface</option>}
              {interfaces.map(i => <option key={`${i.interface}-${i.ip}`} value={i.suggested_cidr}>{i.interface}: {i.ip} ({i.suggested_cidr})</option>)}
            </select>
          </label>
          <label>Mode<br />
            <select aria-label="Mode scan" value={scanMode} onChange={e => setScanMode(e.target.value as "quick" | "extended")}>
              <option value="quick">Quick discovery</option><option value="extended">Extended CCTV ports</option>
            </select>
          </label>
          <label>IP khusus (opsional)<br />
            <input aria-label="IP kamera khusus" placeholder="Contoh: 192.168.50.14" value={targetIp} onChange={e => setTargetIp(e.target.value)} />
          </label>
          <button disabled={!token} onClick={loadInterfaces}>Deteksi ulang interface</button>
        </div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, margin: "12px 0" }}>
          <input aria-label="Konfirmasi otorisasi jaringan" type="checkbox" checked={authorized} onChange={e => setAuthorized(e.target.checked)} />
          Saya berwenang memindai jaringan privat tersebut.
        </label>
        <button className="primary" disabled={!token || busy || !scanCidr || !authorized || (scanState?.status === "running" || (scanJob !== "" && scanState === null))} onClick={startScan}>Mulai scan LAN</button>
        <p>Status: {scanState ? scanState.status : scanJob ? "queued / mengambil hasil" : "belum dijalankan"}{scanState?.status === "completed" ? ` · ${scanState.result.devices.length} host merespons · ${scanState.result.duration_seconds ?? "?"} detik` : ""}</p>
        {scanState?.result?.error && <p>Scan error: {scanState.result.error}</p>}
        {scanState?.result?.devices?.length ? (
          <div style={{ overflowX: "auto" }}><table style={{ width: "100%" }}><thead><tr><th>IP / MAC</th><th>Kategori</th><th>Port dan bukti</th><th>Peringatan</th></tr></thead><tbody>
            {scanState.result.devices.map(d => <tr key={d.ip}>
              <td><strong>{d.ip}</strong><div>{d.mac || "MAC tidak tersedia"}</div></td>
              <td>{d.classification}{d.onvif_ws_discovery ? " · WS-Discovery" : ""}</td>
              <td>{d.open_ports.map(p => <div key={p.port}><strong>{p.port}</strong> {p.hint} ({p.evidence}) {p.banner && <small>{p.banner}</small>}</div>)}</td>
              <td>{d.flags.join(", ") || "Belum ada"}</td>
            </tr>)}
          </tbody></table></div>
        ) : null}
        <p style={{ fontSize: 12, color: "#636d7a" }}>Discovery belum otomatis menambahkan kamera atau menemukan RTSP path/kredensial. Uji ONVIF dan video memakai akses sah pada tahap enrollment. Scan network diperbolehkan hanya setelah GARDA_NETWORK_SCAN_ENABLED=1 pada server lokal.</p>
      </section>
      <h2>Kamera terkonfigurasi</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}>
        {cameras.map((c) => <article key={c.id} style={{ background: "#fff", border: "1px solid #ddd", padding: 12 }}>
          <strong>{c.id}</strong><p>Site: {c.site_id}</p><p>RTSP: {c.rtsp_configured ? "Configured" : "Missing"}</p><p>PTZ: {c.ptz_configured ? "Configured" : "Not configured"}</p><p>Inference: {c.running ? "Running" : "Stopped"}</p>
          {c.last_error && <p>Last error: {c.last_error}</p>}
        </article>)}
      </div>
      <h2 style={{ marginTop: 20 }}>Event candidates (maks. 40)</h2>
      <div style={{ overflowX: "auto" }}><table style={{ width: "100%" }}><thead><tr><th>Time UTC</th><th>Camera</th><th>Kind</th><th>Data</th></tr></thead><tbody>
        {events.map((e) => <tr key={e.id}><td>{e.time_utc}</td><td>{e.camera_id}</td><td>{e.kind}</td><td><code>{JSON.stringify(e.data)}</code></td></tr>)}
      </tbody></table></div>
      <p>Laboratorium saja. Tidak ada autoplay CCTV atau raw biometric data yang dikirim ke browser.</p>
    </section>
  );
}
