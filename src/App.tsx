import { lazy, Suspense, useEffect, useState } from "react";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useNavigate,
  useLocation,
} from "react-router-dom";
import {
  LayoutDashboard,
  Video,
  CirclePlay,
  Bell,
  ScanFace,
  CarFront,
  Map,
  ShieldAlert,
  Sparkles,
  ChartNoAxesCombined,
  FolderLock,
  Network,
  Server,
  ScrollText,
  Settings as SettingsIcon,
  Search,
  ChevronDown,
  Command as CommandIcon,
  Menu,
  LogOut,
  ShieldCheck,
  ArrowUpRight,
} from "lucide-react";
import { StoreProvider, useDemo } from "./store";
import { Badge, Modal } from "./ui";
import { Command, Live, MapPage, Playback, Events } from "./Monitoring";
import { Incidents, AskGarda, Vault, Intelligence } from "./Operations";
import { System, Devices, Audit, Settings } from "./Administration";
const Analytics = lazy(() => import("./Analytics"));
const nav = [
  ["COMMAND", "/command", LayoutDashboard],
  ["LIVE", "/live", Video],
  ["PLAYBACK", "/playback", CirclePlay],
  ["EVENTS", "/events", Bell],
  ["FACES", "/faces", ScanFace],
  ["PLATES", "/plates", CarFront],
  ["MAP", "/map", Map],
  ["INCIDENTS", "/incidents", ShieldAlert],
  ["ASK GARDA", "/ask-garda", Sparkles],
  ["ANALYTICS", "/analytics", ChartNoAxesCombined],
  ["VAULT", "/vault", FolderLock],
  ["DEVICES", "/devices", Network],
  ["SYSTEM", "/system", Server],
  ["AUDIT", "/audit", ScrollText],
  ["SETTINGS", "/settings", SettingsIcon],
] as const;
function Shell() {
  const { state, toast, log, notify } = useDemo();
  const navigate = useNavigate();
  const location = useLocation();
  const [search, setSearch] = useState(false);
  const [query, setQuery] = useState("");
  const [profile, setProfile] = useState(false);
  const [site, setSite] = useState(false);
  const [mobile, setMobile] = useState(false);
  const [loggedOut, setLoggedOut] = useState(false);
  useEffect(() => {
    const f = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearch((v) => !v);
      }
    };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, []);
  useEffect(() => {
    setMobile(false);
  }, [location.pathname]);
  function go(url: string) {
    navigate(url);
    setSearch(false);
    setQuery("");
  }
  if (loggedOut)
    return (
      <div className="login">
        <img src="/logo.png" alt="Pusada TNI" />
        <h1>GARDA</h1>
        <p>PUSADA MONITORING CENTER</p>
        <Badge>Demonstration workspace</Badge>
        <h2>Siap kembali bertugas?</h2>
        <p>Masuk ke sesi demo lokal. Tidak memerlukan kredensial.</p>
        <button
          className="primary"
          onClick={() => {
            setLoggedOut(false);
            log("Demo login", "Operator 01");
          }}
        >
          Enter demo <ArrowUpRight size={18} />
        </button>
      </div>
    );
  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobile ? "open" : ""}`}>
        <NavLink to="/command" className="brand">
          <img src="/logo.png" alt="Logo Aglis Anggah Ahingani Pusada TNI" />
          <div>
            <strong>
              GARDA<span>®</span>
            </strong>
            <small>PUSADA MONITORING CENTER</small>
          </div>
        </NavLink>
        <div className="nav-label">OPERATIONS WORKSPACE</div>
        <nav>
          {nav.map(([name, url, Icon], i) => (
            <NavLink
              key={url}
              to={url}
              className={({ isActive }) =>
                `nav-item ${isActive ? "selected" : ""} ${[4, 8, 11].includes(i) ? "section-start" : ""}`
              }
            >
              <Icon size={18} />
              <span>{name}</span>
              {name === "INCIDENTS" && state.settings.alerts && (
                <b>
                  {
                    state.incidents.filter((i) => i.status !== "resolved")
                      .length
                  }
                </b>
              )}
              {name === "ASK GARDA" && <span className="nav-ai">AI</span>}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <div>
            <ShieldCheck size={17} />
            <span>LOCAL-FIRST. MISSION-READY.</span>
          </div>
          <small>PMC GARDA · Demo v1.0</small>
          <div className="camo" />
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <button
            className="mobile-menu icon-button"
            aria-label="Open navigation"
            onClick={() => setMobile(!mobile)}
          >
            <Menu size={20} />
          </button>
          <span className="topbar-title">
            PUSADA MONITORING CENTER <i /> <b>GARDA</b>
          </span>
          <button className="site-select" onClick={() => setSite(true)}>
            <Map size={15} /> PUSADA HQ <ChevronDown size={13} />
          </button>
          <button className="global-search" onClick={() => setSearch(true)}>
            <Search size={16} />
            <span>Search workspace…</span>
            <kbd>⌘ K</kbd>
          </button>
          <button className="health-link" onClick={() => navigate("/system")}>
            <i /> Operational
          </button>
          <button
            className="notification-button icon-button"
            aria-label="Active notifications"
            onClick={() => {
              if (state.settings.alerts) navigate("/incidents");
              else notify("Notifikasi insiden dinonaktifkan di Settings");
            }}
          >
            <Bell size={18} />
            {state.settings.alerts && <i />}
          </button>
          <button className="profile" onClick={() => setProfile(true)}>
            <span className="avatar">OP</span>
            <span>
              <b>Operator 01</b>
              <small>{state.settings.role}</small>
            </span>
            <ChevronDown size={13} />
          </button>
        </header>
        <main className={location.pathname === '/command' ? 'command-page' : ''}>
          <Suspense fallback={<div className="empty">Memuat Analytics…</div>}>
            <Routes>
              <Route path="/" element={<Navigate to="/command" replace />} />
              <Route path="/command" element={<Command />} />
              <Route path="/live" element={<Live />} />
              <Route path="/playback" element={<Playback />} />
              <Route path="/events" element={<Events />} />
              <Route
                path="/faces"
                element={<Intelligence key="faces" kind="faces" />}
              />
              <Route
                path="/plates"
                element={<Intelligence key="plates" kind="plates" />}
              />
              <Route path="/map" element={<MapPage />} />
              <Route path="/incidents" element={<Incidents />} />
              <Route path="/ask-garda" element={<AskGarda />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/vault" element={<Vault />} />
              <Route path="/devices" element={<Devices />} />
              <Route path="/system" element={<System />} />
              <Route path="/audit" element={<Audit />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/command" replace />} />
            </Routes>
          </Suspense>
          <footer className="app-footer">
            <span>
              <i /> All core services operational{" "}
              <span>· Simulated environment</span>
            </span>
            <span>
              GMT+7 / JAKARTA <b>SECURE LOCAL DEMO</b>
            </span>
          </footer>
        </main>
      </div>
      {toast && (
        <div className="toast" role="status">
          <ShieldCheck size={18} />
          {toast}
        </div>
      )}
      {search && (
        <Modal title="Search workspace" onClose={() => setSearch(false)}>
          <input
            autoFocus
            aria-label="Global search"
            placeholder="Cari modul, event, pelat, insiden…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <div className="search-results">
            {nav
              .filter(([name]) =>
                name.toLowerCase().includes(query.toLowerCase()),
              )
              .map(([name, url, Icon]) => (
                <button key={url} onClick={() => go(url)}>
                  <Icon size={18} />
                  <span>{name}</span>
                  <ArrowUpRight size={15} />
                </button>
              ))}
            {query &&
              state.events
                .filter((e) =>
                  `${e.type} ${e.entity}`
                    .toLowerCase()
                    .includes(query.toLowerCase()),
                )
                .map((e) => (
                  <button
                    key={e.id}
                    onClick={() => go(`/playback?camera=${e.camera}`)}
                  >
                    <Video size={18} />
                    <span>
                      {e.entity} · {e.type}
                    </span>
                    <ArrowUpRight size={15} />
                  </button>
                ))}
            {query &&
              state.incidents
                .filter((i) =>
                  `${i.title} ${i.id}`
                    .toLowerCase()
                    .includes(query.toLowerCase()),
                )
                .map((i) => (
                  <button
                    key={i.id}
                    onClick={() => go(`/incidents?id=${i.id}`)}
                  >
                    <ShieldAlert size={18} />
                    <span>
                      {i.id} · {i.title}
                    </span>
                  </button>
                ))}
          </div>
        </Modal>
      )}
      {profile && (
        <Modal title="Operator profile" onClose={() => setProfile(false)}>
          <div className="identity-detail">
            <span className="avatar">OP</span>
            <div>
              <h3>Operator 01</h3>
              <p>{state.settings.role} · PUSADA HQ</p>
            </div>
          </div>
          <p>Sesi demonstrasi lokal; bukan akun pengguna terautentikasi.</p>
          <div className="actions">
            <button
              onClick={() => {
                setProfile(false);
                navigate("/settings");
              }}
            >
              Settings & roles
            </button>
            <button
              className="danger"
              onClick={() => {
                setProfile(false);
                setLoggedOut(true);
                log("Demo logout", "Operator 01");
              }}
            >
              <LogOut size={16} /> Exit demo
            </button>
          </div>
        </Modal>
      )}
      {site && (
        <Modal title="Select monitoring site" onClose={() => setSite(false)}>
          <button
            className="site-option"
            onClick={() => {
              setSite(false);
              notify("PUSADA HQ dipilih · 8 kamera online");
            }}
          >
            <Map size={24} />
            <span>
              <b>PUSADA HQ</b>
              <p>Jakarta · 8 cameras · single-site demo</p>
            </span>
            <Badge tone="success">Active</Badge>
          </button>
        </Modal>
      )}
    </div>
  );
}
export default function App() {
  return (
    <StoreProvider>
      <Shell />
    </StoreProvider>
  );
}
