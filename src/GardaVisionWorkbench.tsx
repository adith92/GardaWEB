import { useEffect, useState } from "react";

type Camera = { id: string; site_id: string; rtsp_configured: boolean; ptz_configured: boolean; running: boolean; last_error?: string | null };
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
  useEffect(() => { setCameras([]); setEvents([]); }, [token]);

  return (
    <section style={{ padding: 24, color: "#20242d", maxWidth: 1150, margin: "0 auto" }}>
      <h1>GARDA AI Vision | Development Lab</h1>
      <p>Windows / Linux · Backend terpisah · Semua hasil ANPR/wajah adalah kandidat yang perlu verifikasi manusia. Tidak menggunakan data demo GARDAWEB.</p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, margin: "16px 0" }}>
        <input aria-label="Local operator bearer token" type="password" placeholder="Token operator/admin lokal" value={token} onChange={(e) => setToken(e.target.value)} style={{ width: 310 }} />
        <button disabled={!token} onClick={refresh}>Hubungkan & perbarui</button>
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
      <h2>Kamera</h2>
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
