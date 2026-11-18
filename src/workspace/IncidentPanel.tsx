import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { apiRoot, request } from "./api";

type IncidentRow = {
  id: string; title: string; camera_id: string; severity: string;
  status: "open" | "acknowledged" | "resolved"; created_by: string;
  created_at: string; updated_at: string; event_count?: number;
};
type IncidentDetail = IncidentRow & {
  events: { id: string; camera_id: string; kind: string; observed_at: string }[];
  history: { action: string; actor: string; note: string | null; at: string }[];
};
type Manifest = {
  snapshot_count: number; legal_hold: boolean; signed_export: boolean;
  photos: { event_id: string; photo_id: string; label: string; size_bytes: number; sha256: string }[];
};

export default function IncidentPanel({ csrf, reload }: { csrf: string; reload: number }) {
  const [items, setItems] = useState<IncidentRow[]>([]);
  const [status, setStatus] = useState("");
  const [selected, setSelected] = useState<IncidentDetail | null>(null);
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [note, setNote] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const data = await request<{ incidents: IncidentRow[] }>(
        "/api/v1/incidents" + (status ? "?status=" + encodeURIComponent(status) : "")
      );
      setItems(data.incidents);
    } catch (e) { setMessage((e as Error).message); }
  }, [status]);

  useEffect(() => { void refresh(); }, [refresh, reload]);

  async function details(id: string) {
    try {
      setManifest(null);
      setSelected(await request<IncidentDetail>("/api/v1/incidents/" + id));
    } catch (e) { setMessage((e as Error).message); }
  }

  async function action(id: string, actionName: "acknowledge" | "resolve") {
    setBusy(true); setMessage("");
    try {
      const updated = await request<IncidentDetail>(
        "/api/v1/incidents/" + id + "/" + actionName, { method: "POST" }, csrf
      );
      setSelected(updated);
      await refresh();
      setMessage("Perubahan status berhasil dicatat.");
    } catch (e) { setMessage((e as Error).message); }
    finally { setBusy(false); }
  }

  async function addNote(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!selected) return;
    setBusy(true); setMessage("");
    try {
      const updated = await request<IncidentDetail>(
        "/api/v1/incidents/" + selected.id + "/notes",
        { method: "POST", body: JSON.stringify({ note }) }, csrf
      );
      setSelected(updated); setNote(""); setMessage("Catatan disimpan dalam riwayat insiden.");
    } catch (error) { setMessage((error as Error).message); }
    finally { setBusy(false); }
  }

  async function showManifest(id: string) {
    try {
      setManifest(await request<Manifest>("/api/v1/incidents/" + id + "/evidence-manifest"));
    } catch (e) { setMessage((e as Error).message); }
  }

  return <section className="gw-section" aria-label="Insiden operasional">
    <h2>Insiden operasional</h2>
    <p>Data dari API GARDA, bukan simulasi Command Center. Setiap perubahan disimpan dan diaudit.</p>
    <div className="gw-actions">
      <label>Filter status <select value={status} onChange={e => setStatus(e.target.value)}>
        <option value="">Semua</option><option value="open">Baru</option>
        <option value="acknowledged">Ditangani</option><option value="resolved">Selesai</option>
      </select></label>
      <button onClick={() => void refresh()}>Segarkan insiden</button>
    </div>
    {message ? <p role="status" className="gw-notice">{message}</p> : null}
    <div className="gw-table-wrap"><table>
      <thead><tr><th>Waktu</th><th>Kamera</th><th>Judul</th><th>Severity</th><th>Status</th><th>Event</th><th>Aksi</th></tr></thead>
      <tbody>{items.map(item => <tr key={item.id}>
        <td>{new Date(item.created_at).toLocaleString("id-ID")}</td><td>{item.camera_id}</td>
        <td>{item.title}</td><td>{item.severity}</td><td>{item.status}</td><td>{item.event_count ?? 0}</td>
        <td><button onClick={() => void details(item.id)}>Detail</button></td>
      </tr>)}</tbody>
    </table>{items.length === 0 ? <p className="gw-empty-line">Belum ada insiden yang cocok.</p> : null}</div>
    {selected ? <div className="gw-section">
      <h3>{selected.title} · {selected.status}</h3>
      <p>Kamera {selected.camera_id} · Dibuat {new Date(selected.created_at).toLocaleString("id-ID")}
        · {selected.events.length} kejadian terkait</p>
      <div className="gw-actions">
        {selected.status === "open" ? <button disabled={busy} onClick={() => void action(selected.id, "acknowledge")}>Akui insiden</button> : null}
        {selected.status === "acknowledged" ? <button disabled={busy} onClick={() => void action(selected.id, "resolve")}>Selesaikan insiden</button> : null}
        <button onClick={() => void showManifest(selected.id)}>Periksa hash bukti</button>
        <button onClick={() => { setSelected(null); setManifest(null); }}>Tutup detail</button>
      </div>
      {selected.status !== "resolved" ? <form className="gw-form" onSubmit={addNote}>
        <label>Catatan operator <input required maxLength={500} value={note} onChange={e => setNote(e.target.value)} /></label>
        <button disabled={busy || !note.trim()}>Simpan catatan</button>
      </form> : null}
      <h3>Riwayat audit insiden</h3>
      <div className="gw-table-wrap"><table><thead><tr><th>Waktu</th><th>Petugas</th><th>Aksi</th><th>Catatan</th></tr></thead>
        <tbody>{selected.history.map((entry, index) => <tr key={index}>
          <td>{new Date(entry.at).toLocaleString("id-ID")}</td><td>{entry.actor}</td>
          <td>{entry.action}</td><td>{entry.note || "—"}</td>
        </tr>)}</tbody>
      </table></div>
      {manifest ? <div className="gw-section">
        <h3>Snapshot integrity inventory</h3>
        <p>{manifest.snapshot_count} foto. SHA-256 merupakan checksum, bukan tanda tangan digital atau legal hold.</p>
        <div className="gw-table-wrap"><table><thead><tr><th>Bukti</th><th>Ukuran</th><th>SHA-256</th></tr></thead>
          <tbody>{manifest.photos.map(photo => <tr key={photo.photo_id}>
            <td><a target="_blank" rel="noreferrer" href={apiRoot + "/api/v1/events/" + photo.event_id + "/photos/" + photo.photo_id}>{photo.label}</a></td>
            <td>{photo.size_bytes} byte</td><td><code style={{ overflowWrap: "anywhere" }}>{photo.sha256}</code></td>
          </tr>)}</tbody>
        </table></div>
      </div> : null}
    </div> : null}
  </section>;
}
