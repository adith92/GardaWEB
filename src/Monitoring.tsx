import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  Video,
  Siren,
  ScanFace,
  CarFront,
  HardDrive,
  ArrowRight,
  Download,
  Layers,
  Plus,
  Minus,
  Maximize,
  Play,
  Pause,
  SkipForward,
  Bookmark,
  Radio,
  Server,
  Cpu,
  ShieldCheck,
  Camera as CameraIcon,
} from "lucide-react";
import { cameras, useDemo, download, type Camera, type Event } from "./store";
import {
  Badge,
  CameraTile,
  CameraDetail,
  CameraImage,
  Modal,
  PageTitle,
  Panel,
} from "./ui";
import { filterEvents } from "./logic.mjs";
const positions = [
  [49, 86],
  [50, 69],
  [80, 35],
  [51, 46],
  [60, 26],
  [17, 44],
  [89, 16],
  [81, 70],
];
export function SiteMap({
  onCamera,
  large = false,
}: {
  onCamera: (c: Camera) => void;
  large?: boolean;
}) {
  const [zoom, setZoom] = useState(1);
  const [layers, setLayers] = useState(true);
  const [twin, setTwin] = useState(false);
  return (
    <div className={`site-map ${large ? "large" : ""}`}>
      <div className="map-scene" style={{ transform: `scale(${zoom})` }}>
        <img src="/site-map.png" alt="Skema sintetis kawasan PUSADA HQ" />
        {layers &&
          cameras.map((c, i) => (
            <button
              key={c.id}
              className={`map-camera ${i === 5 ? "alert-node" : ""}`}
              style={{
                left: `${positions[i][0]}%`,
                top: `${positions[i][1]}%`,
              }}
              onClick={() => onCamera(c)}
              aria-label={`Buka ${c.id} ${c.name}`}
            >
              <span>
                <CameraIcon size={13} />
              </span>
              <b>{c.id.slice(-2)}</b> {c.name}
              {i === 5 && <i />}
            </button>
          ))}
        {twin && (
          <>
            <span className="tracked one">P-184</span>
            <span className="tracked two">V-027</span>
            <span className="tracked three">P-096</span>
          </>
        )}
      </div>
      <div className="map-controls">
        <button
          aria-label="Toggle camera layer"
          onClick={() => setLayers(!layers)}
          className={layers ? "active" : ""}
        >
          <Layers size={18} />
        </button>
        <button
          aria-label="Zoom in"
          onClick={() => setZoom(Math.min(1.5, zoom + 0.1))}
        >
          <Plus size={18} />
        </button>
        <button
          aria-label="Zoom out"
          onClick={() => setZoom(Math.max(1, zoom - 0.1))}
        >
          <Minus size={18} />
        </button>
      </div>
      <span className="map-caption">
        PUSADA HQ <span>· SITE SCHEMATIC / DEMO</span>
      </span>
      {large && (
        <button
          className={`twin-toggle ${twin ? "primary" : ""}`}
          onClick={() => setTwin(!twin)}
        >
          <Radio size={15} /> Digital Twin Preview · {twin ? "ON" : "OFF"}
        </button>
      )}
      {twin && (
        <span className="preview-note">
          Preview · entitas sintetis, bukan pelacakan nyata
        </span>
      )}
    </div>
  );
}
export function EventDetail({
  event,
  onClose,
}: {
  event: Event;
  onClose: () => void;
}) {
  const { setState, log, notify } = useDemo();
  const nav = useNavigate();
  return (
    <Modal title={`Evidence · ${event.id}`} onClose={onClose}>
      <CameraImage
        camera={cameras.find((c) => c.id === event.camera)!}
        className="detail-image"
      />
      <div className="detail-meta">
        <Badge tone={event.severity}>{event.severity}</Badge>
        <span>{event.time} WIB · 1 Oktober 2026</span>
      </div>
      <h3>{event.type}</h3>
      <p>
        {event.entity} · {event.camera} · Confidence{" "}
        {Math.round(event.confidence * 100)}%
      </p>
      <p className="muted">
        Snapshot sintetis untuk demonstrasi. Tidak merepresentasikan rekaman
        kejadian nyata.
      </p>
      <div className="actions">
        <button
          className="primary"
          onClick={() => {
            setState((s) => ({
              ...s,
              events: s.events.map((e) =>
                e.id === event.id ? { ...e, status: "reviewed" } : e,
              ),
            }));
            log("Evidence reviewed", event.id);
            notify("Event ditandai reviewed");
            onClose();
          }}
        >
          Mark reviewed
        </button>
        <button
          onClick={() => {
            onClose();
            nav(`/playback?camera=${event.camera}`);
          }}
        >
          Open playback
        </button>
        <button
          onClick={() => {
            download(
              `${event.id}.json`,
              JSON.stringify({ ...event, simulated: true }, null, 2),
            );
            log("Evidence exported", event.id);
          }}
        >
          Export metadata
        </button>
      </div>
    </Modal>
  );
}
export function EventTable({
  events,
  onSelect,
  compact = false,
}: {
  events: Event[];
  onSelect: (e: Event) => void;
  compact?: boolean;
}) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>TIME / WIB</th>
            <th>EVENT</th>
            <th>CAMERA</th>
            <th>ENTITY</th>
            <th>SEVERITY</th>
            {!compact && (
              <>
                <th>CONFIDENCE</th>
                <th>STATUS</th>
              </>
            )}
            <th> EVIDENCE</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <tr key={e.id}>
              <td className="mono">{e.time}</td>
              <td>
                <strong>{e.type}</strong>
              </td>
              <td className="mono">{e.camera}</td>
              <td>{e.entity}</td>
              <td>
                <Badge tone={e.severity}>{e.severity}</Badge>
              </td>
              {!compact && (
                <>
                  <td>{Math.round(e.confidence * 100)}%</td>
                  <td>
                    <Badge>{e.status}</Badge>
                  </td>
                </>
              )}
              <td>
                <button className="text-button" onClick={() => onSelect(e)}>
                  View <ArrowRight size={13} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!events.length && (
        <div className="empty">
          Tidak ada event yang cocok. Coba ubah filter.
        </div>
      )}
    </div>
  );
}
export function Command() {
  const { state, updateIncident, log } = useDemo();
  const [camera, setCamera] = useState<Camera | null>(null);
  const [event, setEvent] = useState<Event | null>(null);
  const nav = useNavigate();
  const active = state.incidents.filter((i) => i.status !== "resolved");
  const metrics = [
    {
      name: "Cameras Online",
      value: "8",
      suffix: "/8",
      icon: Video,
      color: "green",
      to: "/live",
      note: "Seluruh kamera terhubung",
    },
    {
      name: "Active Incidents",
      value: String(active.length),
      suffix: "",
      icon: Siren,
      color: "red",
      to: "/incidents",
      note: "Membutuhkan perhatian",
    },
    {
      name: "Unknown Faces",
      value: String(state.faces.filter((f) => f.category === "unknown").length),
      suffix: "",
      icon: ScanFace,
      color: "blue",
      to: "/faces",
      note: "Terdeteksi hari ini",
    },
    {
      name: "Unknown Plates",
      value: String(state.plates.filter((p) => p.status === "unknown").length),
      suffix: "",
      icon: CarFront,
      color: "olive",
      to: "/plates",
      note: "Terdeteksi hari ini",
    },
    {
      name: "Storage Used",
      value: "62",
      suffix: "%",
      icon: HardDrive,
      color: "orange",
      to: "/vault",
      note: "12.4 TB dari 20 TB",
    },
  ];
  return (
    <>
      <PageTitle
        title="Command Overview"
        description="Pantau kawasan. Kenali kejadian. Kendalikan respons."
      >
        <span className="date-label">Kamis, 01 Oktober 2026</span>
        <button
          onClick={() => {
            download(
              "GARDA-command-report.json",
              JSON.stringify(
                {
                  simulated: true,
                  date: "2026-10-01",
                  cameras: 8,
                  activeIncidents: active.length,
                  incidents: state.incidents,
                },
                null,
                2,
              ),
            );
            log("Command report exported", "PUSADA HQ");
          }}
        >
          <Download size={15} /> Export report
        </button>
      </PageTitle>
      <div className="kpi-strip">
        {metrics.map((m) => (
          <Link to={m.to} key={m.name} className="kpi">
            <div className="kpi-top">
              <span>{m.name}</span>
              <m.icon size={18} className={m.color} />
            </div>
            <div className="kpi-value">
              {m.value}
              <span>{m.suffix}</span>
            </div>
            <small>{m.note}</small>
          </Link>
        ))}
      </div>
      <div className="command-columns">
        <div className="command-main">
          <Panel
            title="Site Overview"
            actions={
              <div className="actions">
                <span className="online">
                  <i /> 8 cameras online
                </span>
                <Link className="text-button" to="/map">
                  Open map <ArrowRight size={14} />
                </Link>
              </div>
            }
          >
            <SiteMap onCamera={setCamera} />
            <div className="live-strip-heading">
              <span>
                <i className="live-dot" /> LIVE MONITORING
              </span>
              <Link to="/live" className="text-button">
                View all cameras <ArrowRight size={13} />
              </Link>
            </div>
            <div className="live-strip">
              {cameras.slice(0, 4).map((c) => (
                <CameraTile
                  key={c.id}
                  camera={c}
                  onClick={() => setCamera(c)}
                />
              ))}
            </div>
          </Panel>
        </div>
        <Panel
          title="Active Incidents"
          className="incident-rail"
          actions={<Badge tone="critical">{active.length}</Badge>}
        >
          <div className="rail-subtitle">
            Prioritas respons operasional{" "}
            <Link to="/incidents">
              <ArrowRight size={16} />
            </Link>
          </div>
          {active.slice(0, 3).map((i) => (
            <article className={`incident-card ${i.severity}`} key={i.id}>
              <div className="between">
                <span className="mono muted">{i.id}</span>
                <Badge tone={i.severity}>{i.severity}</Badge>
              </div>
              <button
                className="incident-title"
                onClick={() => nav(`/incidents?id=${i.id}`)}
              >
                {i.title}
              </button>
              <div className="incident-preview">
                <CameraImage camera={cameras.find((c) => c.id === i.camera)!} />
                <div>
                  <b>{cameras.find((c) => c.id === i.camera)?.name}</b>
                  <p>
                    {i.camera} · {i.time} WIB
                  </p>
                  <span>{i.assignee}</span>
                </div>
              </div>
              <div className="between">
                <button
                  className={i.status === "open" ? "small primary" : "small"}
                  onClick={() =>
                    i.status === "open"
                      ? updateIncident(i.id, { status: "acknowledged" })
                      : nav(`/incidents?id=${i.id}`)
                  }
                >
                  {i.status === "open" ? "Acknowledge" : "Investigate"}
                </button>
                <button
                  className="text-button"
                  onClick={() => nav(`/incidents?id=${i.id}`)}
                >
                  Details <ArrowRight size={13} />
                </button>
              </div>
            </article>
          ))}
          {!active.length && (
            <div className="empty">
              <ShieldCheck /> Semua insiden terselesaikan.
            </div>
          )}
          <Link to="/incidents" className="rail-footer">
            Open incident center <ArrowRight size={15} />
          </Link>
        </Panel>
      </div>
      <Panel
        title="Recent Events"
        className="recent-panel"
        actions={
          <Link to="/events" className="text-button">
            All events <ArrowRight size={14} />
          </Link>
        }
      >
        <EventTable
          events={state.events.slice(-5).reverse()}
          onSelect={setEvent}
          compact
        />
      </Panel>
      <div className="infra-strip">
        <Link to="/system">
          <Server size={23} />
          <div>
            <b>Dell PowerEdge R630</b>
            <small className="online">
              <i /> Core services operational
            </small>
          </div>
          <ArrowRight size={15} />
        </Link>
        <Link to="/vault">
          <HardDrive size={23} />
          <div>
            <b>
              Storage pool <span>12.4 / 20 TB</span>
            </b>
            <div className="progress">
              <i style={{ width: "62%" }} />
            </div>
          </div>
          <span>62%</span>
        </Link>
        <Link to="/system">
          <Cpu size={23} />
          <div>
            <b>GPU inference node</b>
            <small>Future Expansion / Not Installed</small>
          </div>
          <ArrowRight size={15} />
        </Link>
      </div>
      {camera && (
        <CameraOverlay camera={camera} onClose={() => setCamera(null)} />
      )}
      {event && <EventDetail event={event} onClose={() => setEvent(null)} />}
    </>
  );
}
export function CameraOverlay({
  camera,
  onClose,
}: {
  camera: Camera;
  onClose: () => void;
}) {
  const nav = useNavigate();
  const { createIncident } = useDemo();
  return (
    <CameraDetail
      camera={camera}
      onClose={onClose}
      onPlayback={() => {
        onClose();
        nav(`/playback?camera=${camera.id}`);
      }}
      onIncident={() => {
        const id = createIncident(camera.id);
        onClose();
        nav(`/incidents?id=${id}`);
      }}
    />
  );
}
export function Live() {
  const [layout, setLayout] = useState(9);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Camera | null>(null);
  const [cycle, setCycle] = useState(false);
  const [offset, setOffset] = useState(0);
  const { notify } = useDemo();
  useEffect(() => {
    if (cycle) {
      const t = setInterval(() => setOffset((n) => (n + 1) % 8), 5000);
      return () => clearInterval(t);
    }
  }, [cycle]);
  const filtered = [
    ...cameras.slice(offset),
    ...cameras.slice(0, offset),
  ].filter((c) =>
    `${c.id} ${c.name}`.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <PageTitle
        title="Live Monitoring"
        description="Delapan sudut pandang. Satu kendali operasional."
      >
        <Badge tone="success">8/8 online</Badge>
        <Badge>Feed sintetis · bukan live CCTV</Badge>
      </PageTitle>
      <div className="toolbar">
        <input
          aria-label="Cari kamera"
          placeholder="Cari nama atau ID kamera…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="segmented">
          {[1, 4, 9, 16].map((n) => (
            <button
              aria-label={`Layout ${n}`}
              className={layout === n ? "active" : ""}
              key={n}
              onClick={() => setLayout(n)}
            >
              {n}
            </button>
          ))}
        </div>
        <button
          className={cycle ? "active" : ""}
          onClick={() => setCycle(!cycle)}
        >
          <Radio size={16} /> Auto-cycle {cycle ? "ON" : "OFF"}
        </button>
        <button
          onClick={() => {
            const el = document.querySelector(".live-wall");
            if (document.fullscreenElement) document.exitFullscreen();
            else
              el?.requestFullscreen().catch(() =>
                notify("Fullscreen tidak tersedia di browser ini"),
              );
          }}
        >
          <Maximize size={16} /> Fullscreen
        </button>
      </div>
      <div
        className="live-wall"
        style={{
          gridTemplateColumns: `repeat(${layout === 1 ? 1 : layout === 4 ? 2 : layout === 9 ? 3 : 4},minmax(0,1fr))`,
        }}
      >
        {filtered.slice(0, layout).map((c) => (
          <CameraTile camera={c} key={c.id} onClick={() => setSelected(c)} />
        ))}
        {filtered.length > 0 && layout > filtered.length && (
          <div className="wall-summary">
            <ShieldCheck size={35} />
            <h3>All cameras connected</h3>
            <p>8 streams available · {layout} slot layout</p>
            <small>Tidak ada kamera tambahan pada dataset.</small>
          </div>
        )}
      </div>
      {!filtered.length && (
        <div className="empty">Tidak ada kamera yang cocok.</div>
      )}
      {selected && (
        <CameraOverlay camera={selected} onClose={() => setSelected(null)} />
      )}
    </>
  );
}
export function MapPage() {
  const [camera, setCamera] = useState<Camera | null>(null);
  return (
    <>
      <PageTitle
        title="Site Map"
        description="Peta kawasan dan posisi kamera · PUSADA HQ"
      >
        <Badge>Skema sintetis · bukan geolokasi nyata</Badge>
      </PageTitle>
      <Panel>
        <SiteMap onCamera={setCamera} large />
      </Panel>
      <div className="map-legend">
        <span>
          <i className="live-dot" /> Kamera online
        </span>
        <span className="red">● Insiden aktif</span>
        <span>Preview digital twin menggunakan entitas sintetis</span>
      </div>
      {camera && (
        <CameraOverlay camera={camera} onClose={() => setCamera(null)} />
      )}
    </>
  );
}
export function Events() {
  const { state, setState, notify, log } = useDemo();
  const [query, setQuery] = useState("");
  const [camera, setCamera] = useState("");
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [date, setDate] = useState("2026-10-01");
  const [event, setEvent] = useState<Event | null>(null);
  const events = filterEvents(state.events, {
    query,
    camera,
    severity,
    status,
    date,
  });
  function simulate() {
    if (state.feedIndex >= 5) {
      notify(
        "Urutan simulasi selesai. Reset demo dari Settings untuk mengulang.",
      );
      return;
    }
    const source = state.events.slice(0, 5)[state.feedIndex];
    setState((s) => ({
      ...s,
      feedIndex: s.feedIndex + 1,
      events: [
        ...s.events,
        { ...source, id: `SIM-${s.feedIndex + 1}`, status: "new" },
      ],
    }));
    log("Simulated event arrived", source.type);
    notify(`Event simulasi: ${source.type}`);
  }
  return (
    <>
      <PageTitle
        title="Detection Events"
        description="Setiap deteksi terhubung ke sumber bukti."
      >
        <button onClick={simulate}>
          <Plus size={16} /> Simulate next event
        </button>
        <button
          onClick={() => {
            download(
              "GARDA-events.json",
              JSON.stringify({ simulated: true, events }, null, 2),
            );
            log("Events exported", String(events.length));
          }}
        >
          <Download size={16} /> Export
        </button>
      </PageTitle>
      <div className="toolbar wrap">
        <input
          aria-label="Cari event"
          placeholder="Cari event, entitas, kamera…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          aria-label="Filter kamera"
          value={camera}
          onChange={(e) => setCamera(e.target.value)}
        >
          <option value="">Semua kamera</option>
          {cameras.map((c) => (
            <option key={c.id}>{c.id}</option>
          ))}
        </select>
        <select
          aria-label="Filter severity"
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
        >
          <option value="">Semua severity</option>
          {["high", "medium", "low"].map((v) => (
            <option key={v}>{v}</option>
          ))}
        </select>
        <select
          aria-label="Filter status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">Semua status</option>
          <option>new</option>
          <option>reviewed</option>
        </select>
        <input
          type="date"
          aria-label="Tanggal event"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <button
          onClick={() => {
            setQuery("");
            setCamera("");
            setSeverity("");
            setStatus("");
            setDate("2026-10-01");
          }}
        >
          Reset filter
        </button>
      </div>
      <Panel title={`${events.length} events`}>
        <EventTable events={events} onSelect={setEvent} />
      </Panel>
      {event && <EventDetail event={event} onClose={() => setEvent(null)} />}
    </>
  );
}
export function Playback() {
  const [params] = useSearchParams();
  const [camera, setCamera] = useState(params.get("camera") || "CAM-01");
  const [date, setDate] = useState("2026-10-01");
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(80000);
  const [speed, setSpeed] = useState(1);
  const [sync, setSync] = useState(false);
  const [bookmarks, setBookmarks] = useState<number[]>([]);
  const { state, log, notify } = useDemo();
  const current = cameras.find((c) => c.id === camera) || cameras[0];
  useEffect(() => {
    if (playing) {
      const id = setInterval(
        () => setTime((t) => (t >= 86399 ? 0 : Math.min(86399, t + speed))),
        1000,
      );
      return () => clearInterval(id);
    }
  }, [playing, speed]);
  const timecode = new Date(time * 1000).toISOString().slice(11, 19);
  return (
    <>
      <PageTitle
        title="Recording Playback"
        description="Tinjau timeline, hubungkan bukti, dan ekspor metadata simulasi."
      >
        <Badge>Simulasi timeline · gambar statis</Badge>
      </PageTitle>
      <div className="toolbar">
        <select
          aria-label="Kamera playback"
          value={camera}
          onChange={(e) => setCamera(e.target.value)}
        >
          {cameras.map((c) => (
            <option value={c.id} key={c.id}>
              {c.id} · {c.name}
            </option>
          ))}
        </select>
        <input
          aria-label="Tanggal playback"
          type="date"
          value={date}
          onChange={(e) => {
            setDate(e.target.value);
            setPlaying(false);
          }}
        />
        <button className={sync ? "active" : ""} onClick={() => setSync(!sync)}>
          Synchronized 4-camera {sync ? "ON" : "OFF"}
        </button>
      </div>
      {date === "2026-10-01" ? (
        <div className={`playback-canvas ${sync ? "sync" : ""}`}>
          {(sync
            ? [current, ...cameras.filter((c) => c.id !== camera).slice(0, 3)]
            : [current]
          ).map((c) => (
            <CameraImage key={c.id} camera={c}>
              <span className="camera-top">
                {c.id} · {c.name}
                <Badge>SIMULATED PLAYBACK</Badge>
              </span>
              <span className="playback-time">
                {date} · {timecode} WIB
              </span>
            </CameraImage>
          ))}
        </div>
      ) : (
        <div className="empty playback-empty">
          Tidak ada rekaman demo pada tanggal ini. Pilih 1 Oktober 2026.
        </div>
      )}
      <Panel className="timeline-panel">
        <div className="between">
          <div className="actions">
            <button
              aria-label={playing ? "Pause" : "Play"}
              disabled={date !== "2026-10-01"}
              onClick={() => setPlaying(!playing)}
            >
              {playing ? <Pause size={18} /> : <Play size={18} />}
            </button>
            <button
              aria-label="Next frame"
              onClick={() => setTime(Math.min(86399, time + 1))}
            >
              <SkipForward size={18} />
            </button>
            <b className="mono">{timecode}</b>
            <select
              aria-label="Playback speed"
              value={speed}
              onChange={(e) => setSpeed(Number(e.target.value))}
            >
              {[0.5, 1, 2, 4].map((n) => (
                <option value={n} key={n}>
                  {n}×
                </option>
              ))}
            </select>
          </div>
          <div className="actions">
            <button
              onClick={() => {
                setBookmarks([...bookmarks, time]);
                notify(`Bookmark ${timecode} ditambahkan`);
              }}
            >
              <Bookmark size={16} /> Bookmark
            </button>
            <button
              className="primary"
              onClick={() => {
                download(
                  `${camera}-clip-demo.json`,
                  JSON.stringify(
                    {
                      simulated: true,
                      camera,
                      date,
                      playhead: timecode,
                      note: "Metadata only. No video attached.",
                    },
                    null,
                    2,
                  ),
                );
                log("Playback metadata exported", camera);
              }}
            >
              <Download size={16} /> Export clip metadata
            </button>
          </div>
        </div>
        <input
          className="timeline-slider"
          aria-label="Timeline position"
          type="range"
          min="0"
          max="86399"
          value={time}
          onChange={(e) => setTime(Number(e.target.value))}
        />
        <div className="timeline-labels">
          {["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"].map(
            (t) => (
              <span key={t}>{t}</span>
            ),
          )}
        </div>
        <div className="event-markers">
          {state.events.slice(0, 5).map((e) => (
            <button
              key={e.id}
              onClick={() => {
                setCamera(e.camera);
                setTime(
                  e.time.split(":").reduce((a, n) => a * 60 + Number(n), 0),
                );
              }}
            >
              <span className={`severity-dot ${e.severity}`} />
              {e.time} · {e.type}
            </button>
          ))}
        </div>
        {bookmarks.length > 0 && (
          <div className="actions wrap">
            {bookmarks.map((b, i) => (
              <button key={i} onClick={() => setTime(b)}>
                <Bookmark size={13} />
                {new Date(b * 1000).toISOString().slice(11, 19)}
              </button>
            ))}
          </div>
        )}
      </Panel>
    </>
  );
}
