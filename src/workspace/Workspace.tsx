import { lazy, Suspense, useCallback, useEffect, useRef, useState, useDeferredValue } from "react";
import type { FormEvent } from "react";
import { Video, ScanFace, CarFront, Settings, LogOut, RefreshCw, ShieldCheck, Download, Search } from "lucide-react";
import { request, apiRoot, ApiError } from "./api";
import type { Actor, Camera, Event, Provider } from "./api";
import "./workspace.css";

const NetworkPanel = lazy(() => import("./NetworkPanel"));
const tabs = ["Live", "Kejadian", "Perangkat", "Jaringan", "Wajah", "Engine", "Update"] as const;
type Tab = typeof tabs[number];
const date = (value: string) => new Date(value).toLocaleString("id-ID");

function Login({ onLogin }: { onLogin: (actor: Actor) => void }) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    const data = new FormData(event.currentTarget);
    try {
      onLogin(await request<Actor>("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ username: data.get("username"), password: data.get("password") }) }));
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  return <main className="gw login-surface"><form onSubmit={submit} className="login-form">
    <img src="/logo.png" alt="GARDA" /><h1>GARDA Workspace</h1><p>Masuk ke server CCTV Anda.</p>
    <label>Nama pengguna<input name="username" autoComplete="username" required maxLength={80}/></label>
    <label>Kata sandi<input name="password" type="password" autoComplete="current-password" required maxLength={256}/></label>
    {error ? <p role="alert" className="gw-error">{error}</p> : null}
    <button className="gw-primary" disabled={busy}>{busy ? "Menghubungkan…" : "Masuk"}</button>
    <small>Akun dibuat melalui setup lokal server GARDA.</small>
  </form></main>;
}

function LiveTile({ camera, tick, act, canOperate }: { camera: Camera; tick: number; act: (path: string) => void; canOperate: boolean }) {
  const [failed, setFailed] = useState(false);
  useEffect(() => { if (camera.online) setFailed(false); }, [camera.online, tick]);
  return <article className="gw-camera"><div className="gw-video">
    {camera.online && !failed ? <img src={`${apiRoot}/api/v1/cameras/${camera.id}/preview.jpg?t=${tick}`} alt={`Live ${camera.name}`} onError={() => setFailed(true)} /> :
      <div className="gw-empty"><Video size={30}/><strong>{camera.running ? "Menunggu gambar" : camera.configured ? "Kamera berhenti" : "Belum dikonfigurasi"}</strong><span>{camera.id}</span></div>}
    <span className={`gw-live ${camera.online && !failed ? "online" : ""}`}>{camera.online && !failed ? "LIVE" : "OFFLINE"}</span>
  </div><div className="gw-camera-info"><div><strong>{camera.name}</strong><small>{camera.face_provider} · {camera.plate_provider}</small></div>
    {canOperate ? <button disabled={!camera.configured} onClick={() => act(`/api/v1/cameras/${camera.id}/${camera.running ? "stop" : "start"}`)}>{camera.running ? "Stop" : "Mulai"}</button> : null}
  </div>{camera.provider_issues.length ? <p className="gw-issue">{camera.provider_issues.join(" · ")}</p> : null}</article>;
}

function Devices({ cameras, actor, refresh, notice }: { cameras: Camera[]; actor: Actor; refresh: () => void; notice: (s: string) => void }) {
  const [selected, setSelected] = useState(cameras[0]?.id || "CAM-01");
  const [busy, setBusy] = useState(false);
  const camera = cameras.find(c => c.id === selected);
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const data = new FormData(form); setBusy(true);
    try {
      await request(`/api/v1/cameras/${selected}`, { method: "PUT", body: JSON.stringify(Object.fromEntries(data)) }, actor.csrf);
      (form.elements.namedItem("rtsp_url") as HTMLInputElement).value = "";
      notice("Konfigurasi tersimpan terenkripsi."); refresh();
    } catch (e) { notice((e as Error).message); } finally { setBusy(false); }
  }
  return <section className="gw-section"><h2>Konfigurasi perangkat</h2><p>Hentikan kamera sebelum mengubah profil. URL tersimpan tidak ditampilkan kembali.</p>
    <form className="gw-form" onSubmit={save} key={selected}>
      <label>Kamera<select value={selected} onChange={e => setSelected(e.target.value)}>{cameras.map(c => <option key={c.id}>{c.id}</option>)}</select></label>
      <label>Nama<input name="name" defaultValue={camera?.name} required maxLength={100}/></label>
      <label>URL RTSP<input name="rtsp_url" type="password" placeholder="rtsp://IP-kamera:port/path" autoComplete="off" required /></label>
      <label>Engine wajah<select name="face_provider" defaultValue={camera?.face_provider}><option value="sface">YuNet + SFace</option><option value="deepface">DeepFace</option><option value="insightface">InsightFace · model berizin</option><option value="presence">Deteksi kehadiran saja</option></select></label>
      <label>Engine plat<select name="plate_provider" defaultValue={camera?.plate_provider}><option value="fastalpr">FastALPR</option><option value="paddleocr">Detector + PaddleOCR</option><option value="off">Nonaktif</option></select></label>
      <button className="gw-primary" disabled={busy || camera?.running}>{busy ? "Menyimpan…" : "Simpan profil"}</button>
    </form></section>;
}

function Faces({ actor, notice }: { actor: Actor; notice: (s: string) => void }) {
  const [busy, setBusy] = useState(false);
  async function enroll(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; setBusy(true);
    try {
      const result = await request<{ id: string; provider: string }>("/api/v1/faces/enroll", { method: "POST", body: new FormData(form) }, actor.csrf);
      notice(`Terdaftar di ${result.provider}. ID pencabutan: ${result.id}`); form.reset();
    } catch (e) { notice((e as Error).message); } finally { setBusy(false); }
  }
  async function revoke(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const data = new FormData(event.currentTarget);
    try { await request(`/api/v1/faces/${data.get("provider")}/${data.get("id")}`, { method: "DELETE" }, actor.csrf); notice("Referensi wajah dicabut."); }
    catch (e) { notice((e as Error).message); }
  }
  return <section className="gw-section"><h2>Referensi wajah</h2><p>Daftarkan satu wajah yang memiliki dasar penggunaan. Hasil pencocokan memerlukan review operator.</p>
    <form className="gw-form" onSubmit={enroll}>
      <label>Nama referensi<input name="label" required maxLength={90}/></label>
      <label>Referensi izin / otorisasi<input name="reference" required maxLength={140}/></label>
      <label>Provider<select name="provider"><option value="sface">SFace</option><option value="deepface">DeepFace</option><option value="insightface">InsightFace</option></select></label>
      <label>Foto tunggal · JPEG/PNG, maksimal 4 MiB<input type="file" name="image" accept="image/jpeg,image/png" required /></label>
      <button className="gw-primary" disabled={busy}>{busy ? "Memproses…" : "Daftarkan referensi"}</button>
    </form><h3>Cabut referensi</h3><form className="gw-form" onSubmit={revoke}>
      <label>Provider<select name="provider"><option value="sface">SFace</option><option value="deepface">DeepFace</option><option value="insightface">InsightFace</option></select></label>
      <label>ID referensi<input name="id" required pattern="[a-f0-9]{32}" /></label><button>Cabut referensi</button>
    </form></section>;
}

export default function Workspace() {
  const [actor, setActor] = useState<Actor | null>(null);
  const [checking, setChecking] = useState(true);
  const [tab, setTab] = useState<Tab>("Live");
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [notice, setNotice] = useState("");
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const [kind, setKind] = useState("");
  const [tick, setTick] = useState(0);
  const [evidence, setEvidence] = useState("");
  const [connectionError, setConnectionError] = useState("");
  const [retry, setRetry] = useState(0);
  const poll = useRef(false);
  const canOperate = !!actor && actor.role !== "viewer";
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    setChecking(true); setConnectionError("");
    request<Actor>("/api/v1/auth/me", { signal: controller.signal }).then(value => { if (active) setActor(value); }).catch(e => {
      if (active && e.name !== "AbortError" && (!(e instanceof ApiError) || e.status !== 401)) {
        setConnectionError("Server GARDA belum terhubung. Periksa layanan lokal atau alamat server.");
      }
    }).finally(() => { if (active) setChecking(false); });
    return () => { active = false; controller.abort(); };
  }, [retry]);
  const refresh = useCallback(async (signal?: AbortSignal) => {
    if (!actor || poll.current || document.hidden) return;
    poll.current = true;
    try {
      const [cameraData, providerData, eventData] = await Promise.all([
        request<{ cameras: Camera[] }>("/api/v1/cameras", { signal }),
        request<{ providers: Provider[] }>("/api/v1/providers", { signal }),
        canOperate ? request<{ events: Event[] }>(`/api/v1/events?q=${encodeURIComponent(deferredQuery)}${kind ? `&kind=${kind}` : ""}`, { signal }) : Promise.resolve({ events: [] }),
      ]);
      setCameras(cameraData.cameras); setProviders(providerData.providers); setEvents(eventData.events); setTick(Date.now());
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        setNotice((e as Error).message);
        if ((e as Error).message.startsWith("Sesi berakhir")) setActor(null);
      }
    }
    finally { poll.current = false; }
  }, [actor, canOperate, deferredQuery, kind]);
  useEffect(() => {
    const controller = new AbortController(); void refresh(controller.signal);
    const timer = window.setInterval(() => void refresh(controller.signal), 3000);
    return () => { controller.abort(); window.clearInterval(timer); };
  }, [refresh]);
  async function act(path: string) {
    try { await request(path, { method: "POST" }, actor?.csrf); setNotice("Permintaan diterima; lihat status gambar aktual."); void refresh(); }
    catch (e) { setNotice((e as Error).message); }
  }
  async function openEvidence(event: Event) {
    try {
      const data = await request<{ photos: { id: string }[] }>(`/api/v1/events/${event.id}/photos`);
      if (!data.photos.length) { setNotice("Tidak ada snapshot untuk kejadian ini."); return; }
      setEvidence(`${apiRoot}/api/v1/events/${event.id}/photos/${data.photos[0].id}`);
    } catch (e) { setNotice((e as Error).message); }
  }
  if (checking) return <main className="gw"><p role="status">Memeriksa sesi…</p></main>;
  if (connectionError) return <main className="gw login-surface"><section className="login-form"><h1>GARDA Workspace</h1><p role="alert">{connectionError}</p><button onClick={() => setRetry(v => v+1)}>Coba hubungkan kembali</button></section></main>;
  if (!actor) return <Login onLogin={setActor}/>;
  const visibleTabs = tabs.filter(t => actor.role === "admin" || (t !== "Perangkat" && t !== "Jaringan" && t !== "Wajah" && (actor.role !== "viewer" || (t !== "Kejadian" && t !== "Update"))));
  return <main className="gw"><header className="gw-header"><a className="gw-brand" href="/workspace"><img src="/logo.png" alt="GARDA"/><span>GARDA<strong>Workspace</strong></span></a>
    <div className="gw-user"><ShieldCheck size={18}/><span>{actor.lab_no_login ? "Admin lokal · Semua akses" : `${actor.name} · ${actor.role}`}</span>{!actor.lab_no_login ? <button aria-label="Keluar" onClick={async () => { try { await request("/api/v1/auth/logout", { method: "POST" }, actor.csrf); setActor(null); setCameras([]); setEvents([]); } catch (e) { setNotice((e as Error).message); } }}><LogOut size={18}/></button> : null}</div>
  </header><nav className="gw-nav">{visibleTabs.map(t => <button key={t} aria-current={tab === t ? "page" : undefined} onClick={() => setTab(t)}>{t}</button>)}</nav>
    <div className="gw-content"><div className="gw-title"><div><h1>{tab === "Live" ? "Pantauan langsung" : tab}</h1><p>{cameras.filter(c => c.online).length} online · {cameras.length} kamera terdaftar</p></div><button onClick={() => void refresh()}><RefreshCw size={16}/> Segarkan</button></div>
      {notice ? <div className="gw-notice" role="status">{notice}<button aria-label="Tutup pesan" onClick={() => setNotice("")}>×</button></div> : null}
      {tab === "Live" ? <div className="gw-grid">{cameras.map(c => <LiveTile key={c.id} camera={c} tick={tick} act={act} canOperate={canOperate}/>)}</div> : null}
      {tab === "Kejadian" && canOperate ? <section><div className="gw-filters"><label><Search size={16}/><input aria-label="Cari plat, nama atau kamera" placeholder="Cari plat, nama atau kamera" value={query} onChange={e => setQuery(e.target.value)}/></label><select aria-label="Jenis kejadian" value={kind} onChange={e => setKind(e.target.value)}><option value="">Semua kejadian</option><option value="face">Wajah</option><option value="plate">Plat</option><option value="motion">Gerakan</option></select></div>
        <div className="gw-table-wrap"><table><thead><tr><th>Waktu</th><th>Kamera</th><th>Jenis</th><th>Hasil kandidat</th><th>Confidence</th><th>Bukti</th></tr></thead><tbody>{events.map(e => <tr key={e.id}><td>{date(e.observed_at)}</td><td>{e.camera_id}</td><td>{e.kind}</td><td>{e.plate_text || e.face_label || "Belum teridentifikasi"}</td><td>{typeof e.confidence === "number" ? `${(e.confidence*100).toFixed(1)}%` : "—"}</td><td><button onClick={() => void openEvidence(e)}>Snapshot</button></td></tr>)}</tbody></table>{events.length === 0 ? <p className="gw-empty-line">Belum ada kejadian yang cocok.</p> : null}</div></section> : null}
      {tab === "Perangkat" && actor.role === "admin" ? <Devices cameras={cameras} actor={actor} refresh={() => void refresh()} notice={setNotice}/> : null}
      {tab === "Jaringan" && actor.role === "admin" ? <Suspense fallback={<p role="status">Membuka scanner…</p>}><NetworkPanel csrf={actor.csrf}/></Suspense> : null}
      {tab === "Wajah" && actor.role === "admin" ? <Faces actor={actor} notice={setNotice}/> : null}
      {tab === "Engine" ? <section className="gw-section"><h2>Provider AI</h2><p>Model dimuat ketika digunakan. Status loaded menunjukkan inisialisasi, sedangkan akurasi membutuhkan pengujian lokasi.</p><div className="gw-table-wrap"><table><thead><tr><th>Provider</th><th>Tugas</th><th>Dependency</th><th>Status</th></tr></thead><tbody>{providers.map(p => <tr key={p.id}><td>{p.id}</td><td>{p.task}</td><td>{p.installed ? "Tersedia" : "Belum terpasang"}</td><td>{p.state}</td></tr>)}</tbody></table></div></section> : null}
      {tab === "Update" && canOperate ? <section className="gw-section"><h2>Distribusi aplikasi</h2><p>Android menggunakan manifest dari server GARDA yang mengambil paket rilis GitHub terverifikasi.</p><div className="gw-actions">{["fold", "standard"].map(channel => <button key={channel} onClick={async () => { try { const result = await request<{ versionName: string }>(`/api/v1/updates/${channel}/manifest.json`); setNotice(`${channel}: versi ${result.versionName}. Instal melalui updater Android.`); } catch (e) { setNotice((e as Error).message); } }}><Download size={16}/> Periksa {channel}</button>)}</div><p>Instalasi lama dengan signing key berbeda memerlukan backup profil dan migrasi sideload manual. Kata sandi kamera harus dimasukkan kembali setelah instalasi baru.</p></section> : null}
    </div>{evidence ? <div className="gw-modal" role="dialog" aria-modal="true" aria-label="Snapshot kejadian"><div><button onClick={() => setEvidence("")}>Tutup snapshot</button><img src={evidence} alt="Snapshot kejadian"/></div></div> : null}
  </main>;
}
