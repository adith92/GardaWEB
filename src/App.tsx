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
  PanelLeftClose,
  PanelLeftOpen,
  Sun,
  Moon,
  ChevronRight,
} from "lucide-react";
import { StoreProvider, useDemo, cameras } from "./store";
import { ErrorBoundary } from "./ErrorBoundary";
import { Badge, CameraImage, Modal } from "./ui";
import { Command, Live, MapPage, Playback, Events } from "./Monitoring";
import { Incidents, AskGarda, Vault, Intelligence } from "./Operations";
import { System, Devices, Audit, Settings } from "./Administration";
const Analytics = lazy(() => import("./Analytics"));
const Workspace = lazy(() => import("./workspace/Workspace"));
const GardaVisionWorkbench = lazy(() => import("./GardaVisionWorkbench"));
const visionEnabled = import.meta.env.DEV && import.meta.env.VITE_GARDA_AI_LAB === "true";
type NavItem = readonly [string, string, typeof LayoutDashboard];
const navGroups: Array<{ label: string; items: NavItem[] }> = [
  { label: "Overview", items: [["COMMAND", "/command", LayoutDashboard]] },
  { label: "Monitoring", items: [["LIVE", "/live", Video], ["PLAYBACK", "/playback", CirclePlay], ["MAP", "/map", Map]] },
  { label: "Response", items: [["EVENTS", "/events", Bell], ["INCIDENTS", "/incidents", ShieldAlert]] },
  { label: "Intelligence", items: [["FACE RECOGNITIONS", "/faces", ScanFace], ["PLATES", "/plates", CarFront], ["ASK GARDA", "/ask-garda", Sparkles], ["ANALYTICS", "/analytics", ChartNoAxesCombined]] },
  { label: "Evidence", items: [["VAULT", "/vault", FolderLock]] },
  { label: "Administration", items: [["DEVICES", "/devices", Network], ["SYSTEM", "/system", Server], ["AUDIT", "/audit", ScrollText], ["SETTINGS", "/settings", SettingsIcon]] },
];
const nav = navGroups.flatMap((group) => group.items);
const defaultExpanded: Record<string, boolean> = { Overview: true, Monitoring: true, Response: true, Intelligence: false, Evidence: false, Administration: false };
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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [thumbsOpen, setThumbsOpen] = useState(true);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(defaultExpanded);
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    try {
      return localStorage.getItem("garda-theme") === "light" ? "light" : "dark";
    } catch {
      return "dark";
    }
  });
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
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("garda-theme", theme);
    } catch {
      // Theme remains active for the current session when storage is unavailable.
    }
  }, [theme]);
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
        <Badge>Ruang kerja demonstrasi · PUSADA KAK</Badge>
        <h2>Siap kembali bertugas?</h2>
        <p>Masuk ke sesi demo lokal GARDA. Tidak memerlukan kredensial.</p>
        <button
          className="primary"
          onClick={() => {
            setLoggedOut(false);
            log("Demo login", "Operator 01");
          }}
        >
          Masuk ke demo <ArrowUpRight size={18} />
        </button>
      </div>
    );
  return (
    <div className={`app-shell ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}>
      <aside className={`sidebar ${mobile ? "open" : ""} ${sidebarCollapsed ? "collapsed" : ""}`}>
        <NavLink to="/command" className="brand">
          <img src="/logo.png" alt="Logo Aglis Anggah Ahingani Pusada TNI" />
          {!sidebarCollapsed && <div>
            <strong>
              GARDA<span>®</span>
            </strong>
            <small>PUSADA MONITORING CENTER</small>
          </div>}
        </NavLink>
        <button
          className="sidebar-toggle icon-button"
          aria-label={sidebarCollapsed ? "Buka sidebar" : "Tutup sidebar"}
          onClick={() => setSidebarCollapsed((value) => !value)}
        >
          {sidebarCollapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
        </button>
        {!sidebarCollapsed && <div className="nav-label">PUSADA · DEMO KAK V2</div>}
        <nav>
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              {!sidebarCollapsed && group.label !== "Overview" && (
                <button
                  className="nav-group-toggle"
                  onClick={() => setExpandedGroups((current) => ({ ...current, [group.label]: !current[group.label] }))}
                  aria-expanded={expandedGroups[group.label]}
                >
                  <ChevronRight size={13} className={expandedGroups[group.label] ? "rotated" : ""} />
                  {group.label}
                </button>
              )}
              {(sidebarCollapsed || group.label === "Overview" || expandedGroups[group.label]) && group.items.map(([name, url, Icon]) => (
                <NavLink key={url} to={url} title={sidebarCollapsed ? name : undefined} className={({ isActive }) => `nav-item ${isActive ? "selected" : ""}`}>
                  <Icon size={18} />
                  {!sidebarCollapsed && <span>{name}</span>}
                  {!sidebarCollapsed && name === "INCIDENTS" && state.settings.alerts && <b>{state.incidents.filter((i) => i.status !== "resolved").length}</b>}
                  {!sidebarCollapsed && name === "ASK GARDA" && <span className="nav-ai">AI</span>}
                </NavLink>
              ))}
            </div>
          ))}
          {visionEnabled && <NavLink to="/ai-vision" className={({ isActive }) => `nav-item ${isActive ? "selected" : ""}`}><ScanFace size={18}/><span>AI VISION LAB</span></NavLink>}
        </nav>
        {!sidebarCollapsed && <>
        <div className="thumbnail-heading">
          <span>CAMERA THUMBNAILS</span>
          <button className="icon-button" aria-label={thumbsOpen ? "Tutup thumbnails" : "Buka thumbnails"} onClick={() => setThumbsOpen((value) => !value)}>
            <ChevronRight size={15} className={thumbsOpen ? "rotated" : ""} />
          </button>
        </div>
        {thumbsOpen && <div className="thumbnail-grid">
          {cameras.slice(0, 6).map((camera) => (
            <button className="thumbnail-card" key={camera.id} title={`Buka ${camera.id}`} onClick={() => { navigate(`/live?camera=${camera.id}`); notify(`${camera.id} dipilih · feed simulasi`); }}>
              <CameraImage camera={camera} />
              <span><b>{camera.id}</b><small>{camera.name}</small></span>
            </button>
          ))}
        </div>}
        <div className="sidebar-foot">
          <div>
            <ShieldCheck size={17} />
            <span>LOCAL-FIRST. MISSION-READY.</span>
          </div>
          <small>PMC GARDA · V2 · Data Demo</small>
          <div className="camo" />
        </div>
        </>}
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
          <a className="stage2-link" href="/garda-stage2.html" target="_blank" rel="noreferrer">
            DEMO TAHAP 2
          </a>
          <button
            className="theme-toggle icon-button"
            aria-label={`Gunakan tema ${theme === "dark" ? "terang" : "gelap"}`}
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
          </button>
          <button className="site-select" onClick={() => setSite(true)}>
            <Map size={15} /> PUSADA HQ <ChevronDown size={13} />
          </button>
          <button className="global-search" onClick={() => setSearch(true)}>
            <Search size={16} />
            <span>Cari modul atau event…</span>
            <kbd>⌘ K</kbd>
          </button>
          <button className="health-link" onClick={() => navigate("/system")}>
            <i /> Sistem operasional
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
              <Route path="/ai-vision" element={visionEnabled ? <GardaVisionWorkbench /> : <Navigate to="/command" replace />} />
              <Route path="*" element={<Navigate to="/command" replace />} />
            </Routes>
          </Suspense>
          <footer className="app-footer">
            <span>
              <i /> All core services operational{" "}
              <span>· Simulated environment</span>
            </span>
            <span>
              GMT+7 / JAKARTA <a href="/garda-stage2.html" target="_blank" rel="noreferrer">TAHAP 2 BRIEF</a> <b>SECURE LOCAL DEMO</b>
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
  const { pathname } = useLocation();
  if (pathname === "/workspace" || pathname.startsWith("/workspace/")) {
    return <Suspense fallback={<main>Memuat GARDA Workspace…</main>}><Workspace /></Suspense>;
  }
  return (
    <StoreProvider>
      <ErrorBoundary><Shell /></ErrorBoundary>
    </StoreProvider>
  );
}

