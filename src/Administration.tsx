import { useState } from "react";
import {
  Cpu,
  HardDrive,
  MemoryStick,
  Network,
  Server,
  ShieldCheck,
  Download,
  RotateCcw,
  Check,
  Activity,
} from "lucide-react";
import { cameras, useDemo, download } from "./store";
import { Badge, Modal, PageTitle, Panel } from "./ui";
export function System() {
  const { notify, log } = useDemo();
  const [checked, setChecked] = useState(false);
  const metrics = [
    {
      name: "CPU utilization",
      value: "24%",
      icon: Cpu,
      percent: 24,
      note: "2 × Intel Xeon · 24 cores",
    },
    {
      name: "Memory",
      value: "38.4 GB",
      icon: MemoryStick,
      percent: 30,
      note: "128 GB DDR4 ECC · 30%",
    },
    {
      name: "Storage pool",
      value: "12.4 TB",
      icon: HardDrive,
      percent: 62,
      note: "20 TB capacity · mirror healthy",
    },
    {
      name: "Network",
      value: "31.1 Mbps",
      icon: Network,
      percent: 31,
      note: "1 Gbps uplink · 0 dropped frames",
    },
  ];
  return (
    <>
      <PageTitle
        title="System Health"
        description="Kesiapan infrastruktur dan layanan inti · telemetri simulasi."
      >
        <button
          onClick={() => {
            setChecked(true);
            notify("Pemeriksaan demo selesai: seluruh layanan inti healthy");
            log("Demo health check", "R630");
          }}
        >
          <Activity size={16} /> Run health check
        </button>
      </PageTitle>
      <div className="system-banner">
        <Server size={38} />
        <div>
          <h2>Dell PowerEdge R630</h2>
          <p>Core node · Proxmox VE / Ubuntu Server · Uptime 32d 14h 08m</p>
        </div>
        <Badge tone="success">
          <Check size={13} />{" "}
          {checked
            ? "Check complete · Healthy"
            : "All core services operational"}
        </Badge>
      </div>
      <div className="system-metrics">
        {metrics.map((m) => (
          <Panel key={m.name}>
            <m.icon size={23} />
            <h3>{m.name}</h3>
            <strong>{m.value}</strong>
            <div className="progress">
              <i style={{ width: `${m.percent}%` }} />
            </div>
            <small>{m.note}</small>
          </Panel>
        ))}
      </div>
      <div className="two-col">
        <Panel title="Service status">
          <table>
            <thead>
              <tr>
                <th>SERVICE</th>
                <th>STATE</th>
                <th>LATENCY / HEALTH</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["PostgreSQL + pgvector", "4 ms"],
                ["Frigate NVR", "8 / 8 streams"],
                ["MediaMTX", "RTSP healthy"],
                ["MQTT broker", "Connected"],
                ["Redis", "1 ms"],
                ["MinIO storage", "Mirror healthy"],
                ["UPS", "38 min runtime"],
              ].map(([n, v]) => (
                <tr key={n}>
                  <td>{n}</td>
                  <td>
                    <Badge tone="success">Healthy</Badge>
                  </td>
                  <td>{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
        <div>
          <Panel title="GPU inference node">
            <div className="gpu-panel">
              <Cpu size={42} />
              <h2>Future Expansion</h2>
              <Badge>Not Installed</Badge>
              <p>
                Node akselerasi AI direncanakan pada fase berikutnya. Demo tidak
                melaporkan pemakaian GPU atau inferensi nyata.
              </p>
            </div>
          </Panel>
          <Panel title="Environmental health">
            <div className="context-list horizontal">
              <div>
                <span>CPU TEMP</span>
                <b>42°C</b>
              </div>
              <div>
                <span>RTSP FAILURES</span>
                <b>0</b>
              </div>
              <div>
                <span>DROPPED FRAMES</span>
                <b>0</b>
              </div>
            </div>
          </Panel>
        </div>
      </div>
    </>
  );
}
const devices = [
  ...cameras.map((c, i) => ({
    id: c.id,
    name: c.name,
    type: "IP Camera",
    ip: `192.168.20.${11 + i}`,
    state: "Online",
    model: c.ptz ? "ONVIF PTZ" : "ONVIF Fixed",
    temperature: "36°C",
    stream: `${c.fps} FPS · ${c.bitrateMbps} Mbps`,
  })),
  {
    id: "SRV-01",
    name: "Dell PowerEdge R630",
    type: "Core server",
    ip: "192.168.10.10",
    state: "Online",
    model: "PowerEdge R630",
    temperature: "42°C",
    stream: "Healthy",
  },
  {
    id: "SW-01",
    name: "Managed Switch",
    type: "Network",
    ip: "192.168.10.2",
    state: "Online",
    model: "24-port PoE",
    temperature: "34°C",
    stream: "1 Gbps",
  },
  {
    id: "UPS-01",
    name: "Rack UPS",
    type: "Power",
    ip: "192.168.10.3",
    state: "Online",
    model: "2200 VA",
    temperature: "28°C",
    stream: "38 min backup",
  },
  {
    id: "NVR-01",
    name: "DVR / NVR integration",
    type: "Recorder",
    ip: "—",
    state: "Placeholder",
    model: "Not configured",
    temperature: "—",
    stream: "Not connected",
  },
  {
    id: "HDD-01",
    name: "Surveillance HDD pool",
    type: "Storage",
    ip: "—",
    state: "Online",
    model: "RAID1 mirror",
    temperature: "33°C",
    stream: "SMART passed",
  },
];
export function Devices() {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<(typeof devices)[number] | null>(
    null,
  );
  const { notify, log } = useDemo();
  return (
    <>
      <PageTitle
        title="Device Inventory"
        description="Kamera, jaringan, server, dan penyimpanan dalam satu inventaris."
      >
        <Badge>{devices.length} demo devices</Badge>
      </PageTitle>
      <div className="toolbar">
        <input
          aria-label="Cari perangkat"
          placeholder="Cari perangkat, jenis, IP…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          onClick={() => {
            download(
              "GARDA-devices.json",
              JSON.stringify({ simulated: true, devices }, null, 2),
            );
            log("Device inventory exported", "All devices");
          }}
        >
          <Download size={16} /> Export inventory
        </button>
      </div>
      <Panel>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>DEVICE</th>
                <th>TYPE</th>
                <th>IP ADDRESS</th>
                <th>STATE</th>
                <th>TEMP</th>
                <th>STREAM / HEALTH</th>
                <th>DETAIL</th>
              </tr>
            </thead>
            <tbody>
              {devices
                .filter((d) =>
                  `${d.name} ${d.type} ${d.ip}`
                    .toLowerCase()
                    .includes(query.toLowerCase()),
                )
                .map((d) => (
                  <tr key={d.id}>
                    <td>
                      <b>{d.name}</b>
                      <small className="block muted">{d.id}</small>
                    </td>
                    <td>{d.type}</td>
                    <td className="mono">{d.ip}</td>
                    <td>
                      <Badge
                        tone={d.state === "Online" ? "success" : "neutral"}
                      >
                        {d.state}
                      </Badge>
                    </td>
                    <td>{d.temperature}</td>
                    <td>{d.stream}</td>
                    <td>
                      <button onClick={() => setSelected(d)}>Inspect</button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </Panel>
      {selected && (
        <Modal title={selected.name} onClose={() => setSelected(null)}>
          <div className="context-list">
            <div>
              <span>MODEL</span>
              <b>{selected.model}</b>
            </div>
            <div>
              <span>NETWORK</span>
              <b>{selected.ip} · demo private address</b>
            </div>
            <div>
              <span>FIRMWARE / UPTIME</span>
              <b>
                {selected.state === "Online"
                  ? "Demo v1.0 · 32d 14h"
                  : "Not configured"}
              </b>
            </div>
            <div>
              <span>STREAM HEALTH</span>
              <b>{selected.stream}</b>
            </div>
          </div>
          <button
            onClick={() => {
              notify(
                selected.state === "Online"
                  ? "Simulasi diagnostik: perangkat healthy"
                  : "Placeholder belum terhubung — tidak ada diagnostik nyata",
              );
              log("Device diagnostic simulated", selected.id);
            }}
          >
            <Activity size={16} /> Run demo diagnostic
          </button>
        </Modal>
      )}
    </>
  );
}
export function Audit() {
  const { state, log } = useDemo();
  const [query, setQuery] = useState("");
  const logs = state.audit.filter((l) =>
    `${l.action} ${l.target}`.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <PageTitle
        title="Audit Trail"
        description="Jejak tindakan operator dalam sesi demo lokal."
      >
        <button
          onClick={() => {
            download(
              "GARDA-audit.json",
              JSON.stringify({ simulated: true, logs }, null, 2),
            );
            log("Audit exported", "Local session");
          }}
        >
          <Download size={16} /> Export audit
        </button>
      </PageTitle>
      <div className="toolbar">
        <input
          aria-label="Cari audit"
          placeholder="Cari aktivitas atau target…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Badge>{logs.length} entries</Badge>
      </div>
      <Panel>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>TIME / WIB</th>
                <th>ACTIVITY</th>
                <th>TARGET</th>
                <th>ACTOR</th>
                <th>RESULT</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l, i) => (
                <tr key={i}>
                  <td className="mono">{l.time}</td>
                  <td>{l.action}</td>
                  <td>{l.target}</td>
                  <td>Operator 01</td>
                  <td>
                    <Badge tone="success">Local demo</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!logs.length && (
            <div className="empty">Tidak ada aktivitas yang cocok.</div>
          )}
        </div>
      </Panel>
    </>
  );
}
export function Settings() {
  const { state, setState, notify, log, reset } = useDemo();
  const [role, setRole] = useState(state.settings.role);
  const [retention, setRetention] = useState(state.settings.retention);
  const [alerts, setAlerts] = useState(state.settings.alerts);
  const [confirm, setConfirm] = useState(false);
  return (
    <>
      <PageTitle
        title="Settings & Roles"
        description="Konfigurasi demonstrasi · tidak memengaruhi sistem operasional."
      />
      <div className="two-col">
        <Panel title="Workspace configuration">
          <form
            className="settings-form"
            onSubmit={(e) => {
              e.preventDefault();
              setState((s) => ({
                ...s,
                settings: { role, retention, alerts },
              }));
              log("Demo settings updated", role);
              notify("Pengaturan demo tersimpan");
            }}
          >
            <label htmlFor="site-name">Site name</label>
            <input id="site-name" value="PUSADA HQ" readOnly />
            <label htmlFor="role">Preview role</label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              {[
                "Command Supervisor",
                "Operator",
                "Investigator",
                "Executive Viewer",
                "System Admin",
                "Auditor",
              ].map((r) => (
                <option key={r}>{r}</option>
              ))}
            </select>
            <small>
              Role hanya mengubah konteks demo. Bukan autentikasi atau
              pembatasan akses nyata.
            </small>
            <label htmlFor="retention">Default retention</label>
            <select
              id="retention"
              value={retention}
              onChange={(e) => setRetention(e.target.value)}
            >
              {["7", "30", "90", "180", "365"].map((d) => (
                <option value={d} key={d}>
                  {d} hari
                </option>
              ))}
            </select>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={alerts}
                onChange={(e) => setAlerts(e.target.checked)}
              />{" "}
              Tampilkan notifikasi insiden pada demo
            </label>
            <button className="primary">
              <Check size={16} /> Save settings
            </button>
          </form>
        </Panel>
        <div>
          <Panel title="Security & demo boundaries">
            <div className="settings-info">
              <ShieldCheck size={28} />
              <h3>Local-first demonstration</h3>
              <p>
                Tidak ada API berbayar, koneksi kamera, pengenalan biometrik,
                atau pengiriman data eksternal.
              </p>
              <p>
                Data disimpan dalam localStorage browser. Jangan masukkan
                informasi rahasia. HTTPS, MFA, RBAC, dan audit yang tahan
                manipulasi memerlukan backend produksi.
              </p>
            </div>
          </Panel>
          <Panel title="Demo data">
            <div className="settings-info">
              <p>
                Reset menghapus perubahan pada demo ini saja dan mengembalikan
                data awal. File sumber proyek tidak berubah.
              </p>
              <button className="danger" onClick={() => setConfirm(true)}>
                <RotateCcw size={15} /> Reset demo data
              </button>
            </div>
          </Panel>
        </div>
      </div>
      {confirm && (
        <Modal title="Reset demo data?" onClose={() => setConfirm(false)}>
          <p>
            Catatan insiden, klasifikasi, metadata upload, folder tambahan, dan
            audit lokal akan dikembalikan ke data awal.
          </p>
          <div className="actions">
            <button onClick={() => setConfirm(false)}>Cancel</button>
            <button
              className="primary"
              onClick={() => {
                reset();
                setRole("Command Supervisor");
                setRetention("30");
                setAlerts(true);
                setConfirm(false);
              }}
            >
              Confirm reset
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
