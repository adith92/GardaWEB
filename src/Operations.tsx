import { useRef, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import {
  Check,
  Download,
  Plus,
  Send,
  Sparkles,
  Folder,
  Upload,
  Share2,
  Archive,
  FileText,
  ChevronRight,
  Shield,
  Search,
  ScanFace,
  CarFront,
  ArrowRight,
} from "lucide-react";
import {
  cameras,
  download,
  useDemo,
  type Event,
  type VaultFile,
} from "./store";
import { Badge, CameraImage, Modal, PageTitle, Panel } from "./ui";
import { EventDetail } from "./Monitoring";
import { answerQuery, prompts } from "./logic.mjs";
export function Incidents() {
  const { state, updateIncident, log, notify } = useDemo();
  const [params, setParams] = useSearchParams();
  const [status, setStatus] = useState("");
  const [query, setQuery] = useState("");
  const [note, setNote] = useState("");
  const [attach, setAttach] = useState(false);
  const [event, setEvent] = useState<Event | null>(null);
  const incidents = state.incidents.filter(
    (i) =>
      (!status || i.status === status) &&
      `${i.id} ${i.title}`.toLowerCase().includes(query.toLowerCase()),
  );
  const current =
    incidents.find((i) => i.id === params.get("id")) || incidents[0];
  return (
    <>
      <PageTitle
        title="Incident Command"
        description="Dari deteksi menjadi tindakan. Semua bukti dalam satu berkas."
      >
        <Badge>
          {state.incidents.filter((i) => i.status !== "resolved").length} active
          cases
        </Badge>
      </PageTitle>
      <div className="toolbar">
        <input
          placeholder="Cari ID atau judul insiden…"
          aria-label="Cari insiden"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          aria-label="Status insiden"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">Semua status</option>
          <option>open</option>
          <option>acknowledged</option>
          <option>resolved</option>
        </select>
      </div>
      <div className="case-layout">
        <Panel
          title={`Incident queue (${incidents.length})`}
          className="case-queue"
        >
          {incidents.map((i) => (
            <button
              key={i.id}
              className={`case-item ${current?.id === i.id ? "selected" : ""}`}
              onClick={() => {
                setParams({ id: i.id });
                setNote("");
              }}
            >
              <div className="between">
                <b className="mono">{i.id}</b>
                <Badge tone={i.severity}>{i.severity}</Badge>
              </div>
              <h3>{i.title}</h3>
              <p>
                {i.camera} · {i.time} WIB
              </p>
              <Badge tone={i.status === "resolved" ? "success" : "neutral"}>
                {i.status}
              </Badge>
            </button>
          ))}
        </Panel>
        {current ? (
          <Panel className="case-body">
            <div className="case-heading">
              <div className="actions">
                <span className="mono muted">{current.id}</span>
                <Badge tone={current.severity}>{current.severity}</Badge>
                <Badge
                  tone={current.status === "resolved" ? "success" : "neutral"}
                >
                  {current.status}
                </Badge>
              </div>
              <h2>{current.title}</h2>
              <p>
                1 Oktober 2026 · {current.time} WIB · {current.camera} · PUSADA
                HQ
              </p>
            </div>
            <div className="case-content">
              <div>
                <div className="ai-summary">
                  <h3>
                    <Sparkles size={16} /> AI summary <Badge>SIMULATED</Badge>
                  </h3>
                  <p>
                    {current.camera === "CAM-06"
                      ? "Aktivitas personel terdeteksi di zona gudang setelah jam operasional. Identitas belum terverifikasi. Operator perlu memeriksa bukti dan mengonfirmasi otorisasi akses."
                      : current.camera === "CAM-07"
                        ? "Kendaraan B 1234 GAR terdeteksi di gerbang belakang. Pelat belum terdaftar dalam direktori. Verifikasi kendaraan dan catatan akses sebelum menutup insiden."
                        : "Diperlukan pemeriksaan manual terhadap kondisi visual kamera. Verifikasi kualitas gambar dan kondisi perangkat sebelum menyelesaikan insiden."}
                  </p>
                </div>
                <h3 className="section-title">Case timeline</h3>
                <ol className="case-timeline">
                  <li>
                    <b>{current.time} · Event detected</b>
                    <p>Deteksi demo diterima dari {current.camera}.</p>
                  </li>
                  <li>
                    <b>{current.time} · Evidence linked</b>
                    <p>Snapshot sintetis tersedia untuk investigasi.</p>
                  </li>
                  {current.status !== "open" && (
                    <li>
                      <b>Acknowledged</b>
                      <p>Respons operator dicatat pada sesi demo.</p>
                    </li>
                  )}
                  {(current.notes || []).map((n, i) => (
                    <li key={i}>
                      <b>Operator note</b>
                      <p>{n}</p>
                    </li>
                  ))}
                  {current.status === "resolved" && (
                    <li>
                      <b>Resolved</b>
                      <p>Insiden ditutup oleh operator pada demo.</p>
                    </li>
                  )}
                </ol>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (note.trim()) {
                      updateIncident(current.id, {
                        notes: [...(current.notes || []), note.trim()],
                      });
                      setNote("");
                    }
                  }}
                >
                  <label htmlFor="case-note">Catatan investigasi</label>
                  <textarea
                    id="case-note"
                    placeholder="Tulis hasil verifikasi atau tindak lanjut…"
                    value={note}
                    maxLength={1000}
                    onChange={(e) => setNote(e.target.value)}
                    required
                  />
                  <button type="submit">
                    <Plus size={15} /> Add note
                  </button>
                </form>
              </div>
              <aside className="evidence-column">
                <h3>Evidence</h3>
                <CameraImage
                  camera={cameras.find((c) => c.id === current.camera)!}
                />
                <p>Snapshot sintetis · {current.camera}</p>
                <button
                  className="text-button"
                  onClick={() =>
                    setEvent(
                      state.events.find((e) => e.camera === current.camera) ||
                        state.events[0],
                    )
                  }
                >
                  Open evidence <ArrowRight size={14} />
                </button>
                <h3>Assigned operator</h3>
                <select
                  aria-label="Assigned operator"
                  value={current.assignee}
                  onChange={(e) =>
                    updateIncident(current.id, { assignee: e.target.value })
                  }
                >
                  {[
                    "Unassigned",
                    "Operator 01",
                    "Operator 02",
                    "Supervisor",
                  ].map((n) => (
                    <option key={n}>{n}</option>
                  ))}
                </select>
                <h3>Linked entities</h3>
                <Link to={current.camera === "CAM-07" ? "/plates" : "/faces"}>
                  {current.camera === "CAM-07" ? "B 1234 GAR" : "Unknown #18"}{" "}
                  <ArrowRight size={13} />
                </Link>
                <h3>Attachments</h3>
                {(current.evidence || []).map((id) => (
                  <button
                    className="text-button"
                    key={id}
                    onClick={() =>
                      setEvent(state.events.find((e) => e.id === id)!)
                    }
                  >
                    {id}
                  </button>
                ))}
                <button onClick={() => setAttach(true)}>
                  <Plus size={15} /> Attach evidence
                </button>
              </aside>
            </div>
            <div className="case-actions">
              <button
                className="primary"
                disabled={current.status !== "open"}
                onClick={() =>
                  updateIncident(current.id, { status: "acknowledged" })
                }
              >
                <Check size={16} /> Acknowledge
              </button>
              <button
                onClick={() =>
                  updateIncident(current.id, {
                    status: current.status === "resolved" ? "open" : "resolved",
                  })
                }
              >
                {current.status === "resolved"
                  ? "Reopen case"
                  : "Resolve incident"}
              </button>
              <button
                onClick={() => {
                  download(
                    `${current.id}-demo-package.json`,
                    JSON.stringify(
                      {
                        simulated: true,
                        incident: current,
                        evidence: state.events.filter(
                          (e) =>
                            e.camera === current.camera ||
                            (current.evidence || []).includes(e.id),
                        ),
                        notice:
                          "Demo metadata package; no source video or forensic integrity guarantee.",
                      },
                      null,
                      2,
                    ),
                  );
                  log("Incident package exported", current.id);
                  notify("Paket metadata demo diunduh");
                }}
              >
                <Download size={16} /> Export package
              </button>
            </div>
          </Panel>
        ) : (
          <Panel>
            <div className="empty">Tidak ada insiden pada filter ini.</div>
          </Panel>
        )}
      </div>
      {attach && current && (
        <Modal title="Attach event evidence" onClose={() => setAttach(false)}>
          <div className="attachment-list">
            {state.events.map((e) => (
              <button
                key={e.id}
                onClick={() => {
                  updateIncident(current.id, {
                    evidence: [...new Set([...(current.evidence || []), e.id])],
                  });
                  setAttach(false);
                }}
              >
                <FileText size={20} />
                <span>
                  <b>{e.id}</b>
                  <p>
                    {e.type} · {e.camera}
                  </p>
                </span>
                <Plus size={16} />
              </button>
            ))}
          </div>
        </Modal>
      )}
      {event && <EventDetail event={event} onClose={() => setEvent(null)} />}
    </>
  );
}
export function AskGarda() {
  const { state, log } = useDemo();
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<
    { query: string; text: string; refs: string[] }[]
  >([]);
  const [event, setEvent] = useState<Event | null>(null);
  function ask(q: string) {
    if (!q.trim()) return;
    setHistory((h) => [
      ...h,
      { query: q, ...answerQuery(q, state.incidents, state.plates) },
    ]);
    setInput("");
    log("Ask GARDA demo query", q);
  }
  return (
    <>
      <PageTitle
        title="Ask GARDA"
        description="Pertanyaan operasional. Jawaban terhubung bukti."
      >
        <Badge>
          <Sparkles size={12} /> Deterministic demo · AI offline
        </Badge>
      </PageTitle>
      <div className="ask-layout">
        <Panel className="ask-main">
          {!history.length ? (
            <div className="ask-welcome">
              <div className="ask-symbol">
                <Sparkles size={35} />
              </div>
              <h2>Apa yang perlu Anda ketahui?</h2>
              <p>
                Telusuri kejadian, kendaraan, dan identitas dari satu pusat
                komando.
              </p>
              <small>
                Jawaban simulasi berdasarkan dataset lokal. Tidak ada model AI
                yang dihubungkan.
              </small>
            </div>
          ) : (
            <div className="ask-results">
              {history.map((h, i) => (
                <article key={i}>
                  <h3>
                    <Search size={16} />
                    {h.query}
                  </h3>
                  <div className="answer">
                    <span className="answer-label">
                      <Sparkles size={16} /> GARDA ANALYSIS{" "}
                      <Badge>SIMULATED</Badge>
                    </span>
                    <p>{h.text}</p>
                    <div className="actions wrap">
                      {h.refs.map((id) => (
                        <button
                          key={id}
                          onClick={() =>
                            setEvent(state.events.find((e) => e.id === id)!)
                          }
                        >
                          <FileText size={14} />
                          {id} <ArrowRight size={12} />
                        </button>
                      ))}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
          <div className="query-suggestions">
            <span>PERTANYAAN OPERASIONAL</span>
            {prompts.map((q) => (
              <button key={q} onClick={() => ask(q)}>
                {q}
                <ArrowRight size={15} />
              </button>
            ))}
          </div>
          <form
            className="ask-form"
            onSubmit={(e) => {
              e.preventDefault();
              ask(input);
            }}
          >
            <Search size={20} />
            <input
              aria-label="Pertanyaan Ask GARDA"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Tanyakan kejadian, kendaraan, atau laporan shift…"
              required
            />
            <button
              className="primary icon-button"
              aria-label="Kirim pertanyaan"
            >
              <Send size={19} />
            </button>
          </form>
        </Panel>
        <aside>
          <Panel title="Active Context">
            <div className="context-list">
              <div>
                <span>SITE</span>
                <b>PUSADA HQ</b>
              </div>
              <div>
                <span>DATE RANGE</span>
                <b>01 Oktober 2026</b>
                <small>Dataset 22:14–22:22 WIB</small>
              </div>
              <div>
                <span>CAMERAS</span>
                <b>8 cameras connected</b>
              </div>
              <div>
                <span>ACCESS</span>
                <b>{state.settings.role}</b>
              </div>
            </div>
          </Panel>
          <div className="context-notice">
            <Shield size={20} />
            <h3>Evidence-first intelligence</h3>
            <p>
              Setiap jawaban yang didukung data memiliki referensi bukti yang
              bisa dibuka dan diperiksa.
            </p>
            <small>
              Semua orang, kendaraan, dan kejadian dalam demo bersifat fiktif.
            </small>
          </div>
        </aside>
      </div>
      {event && <EventDetail event={event} onClose={() => setEvent(null)} />}
    </>
  );
}
export function Vault() {
  const { state, setState, notify, log } = useDemo();
  const [folder, setFolder] = useState("Incident Evidence");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const [newFolder, setNewFolder] = useState(false);
  const [name, setName] = useState("");
  const [share, setShare] = useState(false);
  const [shareRole, setShareRole] = useState('Investigator · read-only');
  const [shareExpiry, setShareExpiry] = useState('24 jam');
  const upload = useRef<HTMLInputElement>(null);
  const files = state.files.filter(
    (f) =>
      (folder === "Archive"
        ? f.archived
        : !f.archived && f.folder === folder) &&
      f.name.toLowerCase().includes(query.toLowerCase()),
  );
  const current = files.find((f) => f.id === selected);
  function addFiles(list: FileList | null) {
    if (!list?.length) return;
    const added = Array.from(list).map((f, i) => ({
      id: `UP-${Date.now()}-${i}`,
      name: f.name,
      folder: folder === "Archive" ? "Personal" : folder,
      type: f.name.split(".").pop()?.toUpperCase() || "FILE",
      size: `${(f.size / 1024).toFixed(1)} KB`,
      owner: "Operator 01",
      retention: `${state.settings.retention} hari`,
    }));
    setState((s) => ({ ...s, files: [...s.files, ...added] }));
    log("Simulated upload metadata", added.map((f) => f.name).join(", "));
    notify(
      `${added.length} metadata file ditambahkan. Isi file tidak diunggah atau disimpan.`,
    );
    if (upload.current) upload.current.value = "";
  }
  return (
    <>
      <PageTitle
        title="GARDA Vault"
        description="Bukti terorganisir. Akses terkendali. Penyimpanan lokal."
      >
        <button onClick={() => setNewFolder(true)}>
          <Plus size={16} /> New folder
        </button>
        <button className="primary" onClick={() => upload.current?.click()}>
          <Upload size={16} /> Upload
        </button>
        <input
          ref={upload}
          type="file"
          multiple
          hidden
          onChange={(e) => addFiles(e.target.files)}
        />
      </PageTitle>
      <div className="vault-layout">
        <Panel className="folder-tree">
          <div className="folder-label">WORKSPACE</div>
          {[...state.folders, "Archive"].map((f) => (
            <button
              key={f}
              className={folder === f ? "selected" : ""}
              onClick={() => {
                setFolder(f);
                setSelected(null);
              }}
            >
              {f === "Archive" ? <Archive size={18} /> : <Folder size={18} />}{" "}
              {f}
            </button>
          ))}
          <div className="vault-storage">
            <HardDriveIcon />
            <h3>Storage pool</h3>
            <b>
              12.4 TB <span>/ 20 TB</span>
            </b>
            <div className="storage-stack">
              <i />
              <i />
              <i />
            </div>
            <p>
              <span>Hot</span>
              <b>0.8 TB</b>
            </p>
            <p>
              <span>Warm</span>
              <b>10.8 TB</b>
            </p>
            <p>
              <span>Archive</span>
              <b>0.8 TB</b>
            </p>
            <small>Utilisasi simulasi · 62%</small>
          </div>
        </Panel>
        <Panel className="vault-files">
          <div className="panel-head">
            <div className="breadcrumb">
              GARDA Vault <ChevronRight size={14} />
              <b>{folder}</b>
            </div>
            <input
              aria-label="Cari file"
              placeholder="Cari file…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="vault-toolbar">
            <span>{files.length} files</span>
            <div className="actions">
              <button disabled={!current} onClick={() => setShare(true)}>
                <Share2 size={15} /> Share
              </button>
              <button
                disabled={!current}
                onClick={() => {
                  setState((s) => ({
                    ...s,
                    files: s.files.map((f) =>
                      f.id === current?.id
                        ? { ...f, archived: !f.archived }
                        : f,
                    ),
                  }));
                  log(
                    folder === "Archive" ? "File restored" : "File archived",
                    current!.name,
                  );
                  setSelected(null);
                  notify(
                    folder === "Archive"
                      ? "File dikembalikan ke folder asal"
                      : "File dipindahkan ke Archive",
                  );
                }}
              >
                <Archive size={15} />
                {folder === "Archive" ? "Restore" : "Archive"}
              </button>
            </div>
          </div>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>NAME</th>
                  <th>TYPE</th>
                  <th>OWNER</th>
                  <th>SIZE</th>
                  <th>RETENTION</th>
                  <th>ACCESS</th>
                </tr>
              </thead>
              <tbody>
                {files.map((f) => (
                  <tr
                    className={selected === f.id ? "selected-row" : ""}
                    key={f.id}
                  >
                    <td>
                      <button
                        className="file-button"
                        onClick={() => setSelected(f.id)}
                      >
                        <FileText size={20} />
                        {f.name}
                      </button>
                    </td>
                    <td>{f.type}</td>
                    <td>{f.owner}</td>
                    <td>{f.size}</td>
                    <td>{f.retention}</td>
                    <td>
                      <Badge>{f.shared ? "Shared demo" : "Private"}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!files.length && (
            <div className="empty">
              <Folder size={28} />
              <h3>Folder masih kosong</h3>
              <p>Tambahkan metadata file untuk mencoba alur Vault.</p>
            </div>
          )}
          <div
            className="drop-zone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              addFiles(e.dataTransfer.files);
            }}
          >
            <Upload size={20} />
            <span>
              Drag & drop file di sini, atau{" "}
              <button
                className="text-button"
                onClick={() => upload.current?.click()}
              >
                pilih file
              </button>
            </span>
            <small>Simulasi metadata saja · tidak dikirim ke server</small>
          </div>
          {current && (
            <div className="file-details">
              <div>
                <h3>{current.name}</h3>
                <p>
                  Modified 01 Oct 2026 · Retention {current.retention} ·{" "}
                  {current.owner}
                </p>
                <small>
                  Demo metadata preview. Version 1 · no stored file payload.
                  {current.shared && ` Shared: ${current.shareRole || 'Internal'} · Expiry: ${current.shareExpiry || '24 jam'}.`}
                </small>
              </div>
              <button
                onClick={() => {
                  download(
                    `${current.name}.metadata.json`,
                    JSON.stringify({ simulated: true, ...current }, null, 2),
                  );
                  log("Vault metadata exported", current.name);
                }}
              >
                <Download size={16} /> Download metadata
              </button>
            </div>
          )}
        </Panel>
      </div>
      {newFolder && (
        <Modal title="New folder" onClose={() => setNewFolder(false)}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const n = name.trim();
              if (!n) return;
              if (
                [...state.folders, "Archive"].some(
                  (f) => f.toLowerCase() === n.toLowerCase(),
                )
              ) {
                notify("Nama folder sudah digunakan");
                return;
              }
              setState((s) => ({ ...s, folders: [...s.folders, n] }));
              setFolder(n);
              setName("");
              setNewFolder(false);
              log("Folder created", n);
              notify("Folder dibuat");
            }}
          >
            <label htmlFor="folder-name">Nama folder</label>
            <input
              id="folder-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={60}
            />
            <button className="primary">Create folder</button>
          </form>
        </Modal>
      )}
      {share && current && (
        <Modal title="Share file · demo only" onClose={() => setShare(false)}>
          <p>{current.name}</p>
          <p>
            Berbagi internal disimulasikan; tidak membuat tautan publik atau
            mengirim file.
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setState((s) => ({
                ...s,
                files: s.files.map((f) =>
                  f.id === current.id ? { ...f, shared: true, shareRole, shareExpiry } : f,
                ),
              }));
              log("Simulated internal share", current.name);
              setShare(false);
              notify("Akses berbagi internal ditandai pada demo");
            }}
          >
            <label htmlFor="share-role">Akses penerima</label>
            <select id="share-role" value={shareRole} onChange={e => setShareRole(e.target.value)}>
              <option>Investigator · read-only</option>
              <option>Supervisor · read-only</option>
            </select>
            <label htmlFor="expiry">Masa berlaku demo</label>
            <select id="expiry" value={shareExpiry} onChange={e => setShareExpiry(e.target.value)}>
              <option>24 jam</option>
              <option>7 hari</option>
            </select>
            <button className="primary">Confirm demo share</button>
          </form>
        </Modal>
      )}
    </>
  );
}
function HardDriveIcon() {
  return <Archive size={22} />;
}
export function Intelligence({ kind }: { kind: "faces" | "plates" }) {
  const { state, setState, log, notify } = useDemo();
  const [tab, setTab] = useState("all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState("");
  const face = kind === "faces";
  const categories = face
    ? ["all", "known", "unknown", "watchlist"]
    : ["all", "registered", "unknown", "watchlist"];
  const faces = state.faces.filter(
    (f) =>
      (tab === "all" || f.category === tab) &&
      f.name.toLowerCase().includes(query.toLowerCase()),
  );
  const plates = state.plates.filter(
    (p) =>
      (tab === "all" || p.status === tab) &&
      `${p.plate} ${p.vehicle}`.toLowerCase().includes(query.toLowerCase()),
  );
  const person = state.faces.find((f) => f.id === selected);
  const vehicle = state.plates.find((p) => p.plate === selected);
  function classify(category: string) {
    setState((s) =>
      face
        ? {
            ...s,
            faces: s.faces.map((f) =>
              f.id === selected ? { ...f, category } : f,
            ),
          }
        : {
            ...s,
            plates: s.plates.map((p) =>
              p.plate === selected ? { ...p, status: category } : p,
            ),
          },
    );
    log("Classification updated", selected);
    notify("Klasifikasi demo diperbarui");
    setSelected("");
  }
  return (
    <>
      <PageTitle
        title={face ? "Face Intelligence" : "Vehicle Intelligence"}
        description={
          face
            ? "Direktori identitas dan jejak kamera. Seluruh identitas bersifat fiktif."
            : "Log pelat, riwayat akses, dan kendaraan di dalam kawasan."
        }
      >
        <Badge>Data sintetis · bukan pengenalan nyata</Badge>
      </PageTitle>
      <div className="toolbar">
        <div className="segmented">
          {categories.map((c) => (
            <button
              key={c}
              className={tab === c ? "active" : ""}
              onClick={() => setTab(c)}
            >
              {c === "all"
                ? "All records"
                : c === "unknown"
                  ? "Unknown queue"
                  : c}
            </button>
          ))}
        </div>
        <input
          aria-label={face ? "Cari identitas" : "Cari pelat"}
          placeholder={face ? "Cari nama…" : "Cari pelat atau kendaraan…"}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {face ? (
        <div className="face-grid">
                {faces.map((f) => (
            <button
              className="person-card"
              key={f.id}
              onClick={() => setSelected(f.id)}
            >
              <div className={`person-avatar avatar-${state.faces.findIndex(person => person.id === f.id)}`}>
                <ScanFace size={58} />
                <span>
                  {f.name
                    .split(" ")
                    .map((x) => x[0])
                    .join("")}
                </span>
                <small>SYNTHETIC IDENTITY</small>
              </div>
              <div className="person-body">
                <div className="between">
                  <h3>{f.name}</h3>
                  <Badge tone={f.category === "known" ? "success" : "medium"}>
                    {f.category}
                  </Badge>
                </div>
                <p>
                  {f.id} · Confidence {Math.round(f.confidence * 100)}%
                </p>
                <div className="between">
                  <span>
                    {f.camera} · {f.lastSeen}
                  </span>
                  <ArrowRight size={16} />
                </div>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <Panel>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>PLATE</th>
                  <th>VEHICLE</th>
                  <th>STATUS</th>
                  <th>FIRST SEEN</th>
                  <th>LAST SEEN</th>
                  <th>CURRENT STATE</th>
                  <th>ENTRY GATE</th>
                </tr>
              </thead>
              <tbody>
                {plates.map((p) => (
                  <tr key={p.plate}>
                    <td>
                      <button
                        className="plate-number"
                        onClick={() => setSelected(p.plate)}
                      >
                        {p.plate}
                      </button>
                    </td>
                    <td>{p.vehicle}</td>
                    <td>
                      <Badge
                        tone={p.status === "unknown" ? "medium" : "success"}
                      >
                        {p.status}
                      </Badge>
                    </td>
                    <td>{p.firstSeen}</td>
                    <td>{p.lastSeen}</td>
                    <td>{p.state}</td>
                    <td>{p.gate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
      {(face ? !faces.length : !plates.length) && (
        <div className="empty">
          Tidak ada data pada kategori atau pencarian ini.
        </div>
      )}
      {selected && (person || vehicle) && (
        <Modal
          title={face ? person!.name : vehicle!.plate}
          onClose={() => setSelected("")}
        >
          {face ? (
            <div className="identity-detail">
              <ScanFace size={54} />
              <div>
                <h3>{person!.name}</h3>
                <p>
                  Confidence {Math.round(person!.confidence * 100)}% ·{" "}
                  {person!.category}
                </p>
              </div>
            </div>
          ) : (
            <>
              <CameraImage
                className="detail-image"
                camera={cameras[vehicle!.gate === "Rear Gate" ? 6 : 2]}
              />
              <h3>
                <CarFront size={18} /> {vehicle!.vehicle} · {vehicle!.plate}
              </h3>
              <p>
                Status: {vehicle!.state} · Parking duration{" "}
                {vehicle!.state === "inside"
                  ? "berjalan sejak " + vehicle!.firstSeen
                  : "10 jam 14 menit"}
              </p>
            </>
          )}
          <h3>{face ? "Camera journey" : "Entry / exit history"}</h3>
          <ol className="case-timeline">
            <li>
              <b>
                {face ? person!.lastSeen : vehicle!.firstSeen} ·{" "}
                {face ? person!.camera : vehicle!.gate}
              </b>
              <p>
                {face
                  ? "Last known sighting in demo dataset"
                  : "Entry recorded"}
              </p>
            </li>
            {!face && (
              <li>
                <b>
                  {vehicle!.lastSeen} ·{" "}
                  {vehicle!.state === "inside"
                    ? "Last seen inside"
                    : "Exit recorded"}
                </b>
                <p>{vehicle!.vehicle}</p>
              </li>
            )}
          </ol>
          <p className="muted">
            Hanya jejak yang tersedia dalam data ditampilkan. Tidak ada lintasan
            tambahan yang diasumsikan.
          </p>
          <div className="actions wrap">
            <button onClick={() => classify("watchlist")}>
              Add to watchlist
            </button>
            <button onClick={() => classify(face ? "known" : "registered")}>
              Confirm {face ? "known identity" : "registered vehicle"}
            </button>
            <button onClick={() => classify("unknown")}>Mark unknown</button>
            <Link className="button" to="/incidents">
              Related incidents
            </Link>
          </div>
        </Modal>
      )}
    </>
  );
}
